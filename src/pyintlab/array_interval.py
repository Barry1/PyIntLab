"""
Numpy-basierte Intervall-Arrays mit garantierter Outward Rounding.
Unterstützt Linux, macOS und Windows.

Architektur:
- Nutzt structured dtype: [('lowerbound', '<f8'), ('upperbound', '<f8')]
- ScalarInterval ist die Referenz für Korrektheit.
- RoundingContext steuert fesetround (Unix) bzw. _controlfp (Windows).
"""

from __future__ import annotations

import ctypes
import platform
from typing import Tuple, Union

import numpy as np

# --- Platform-specific Rounding Setup ---
_OS = platform.system()


class RoundingMode:
    TONEAREST = 0
    DOWNWARD = 1
    UPWARD = 2
    TOWARDZERO = 3


_HAS_ROUNDING_CONTROL = False

if _OS == "Windows":
    try:
        _libc = ctypes.windll.msvcrt
        _HAS_ROUNDING_CONTROL = True
    except Exception:
        _HAS_ROUNDING_CONTROL = False
else:
    try:
        _libc = ctypes.CDLL(None)
        _fesetround = _libc.fesetround
        _fesetround.argtypes = [ctypes.c_int]
        _fesetround.restype = ctypes.c_int
        _HAS_ROUNDING_CONTROL = True
    except Exception:
        _HAS_ROUNDING_CONTROL = False


def set_rounding_mode(mode: int):
    if not _HAS_ROUNDING_CONTROL:
        return
    if _OS == "Windows":
        # Windows: _control87(value, mask)
        # Rounding control bits are 10-11. Mask is 0x0300.
        _libc._control87(mode << 10, 0x0300)
    else:
        _fesetround(mode)


class RoundingContext:
    """Context manager to temporarily change the floating point rounding mode."""

    def __init__(self, mode: int):
        self.mode = mode
        self.old_mode = RoundingMode.TONEAREST

    def __enter__(self):
        if _HAS_ROUNDING_CONTROL:
            set_rounding_mode(self.mode)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if _HAS_ROUNDING_CONTROL:
            set_rounding_mode(RoundingMode.TONEAREST)


# --- Structured dtype ---
scalar_interval_dtype = np.dtype(
    [("lowerbound", "<f8"), ("upperbound", "<f8")]
)


class ArrayInterval:
    """
    Represents an array of intervals using a NumPy structured array.

    Attributes:
        _arr (np.ndarray): The underlying structured array.
    """

    def __init__(self, data: Union[list, np.ndarray]):
        if isinstance(data, np.ndarray):
            if data.dtype == scalar_interval_dtype:
                self._arr = data
            else:
                # Try to convert if it's a 2D array of shape (N, 2)
                if data.ndim == 2 and data.shape[1] == 2:
                    res = np.empty(data.shape[0], dtype=scalar_interval_dtype)
                    res["lowerbound"] = data[:, 0]
                    res["upperbound"] = data[:, 1]
                    self._arr = res
                else:
                    raise ValueError("Invalid data type for ArrayInterval")
        else:
            # Assume list of tuples/lists
            self._arr = np.array(data, dtype=scalar_interval_dtype)

        # Validate intervals
        if np.any(self._arr["lowerbound"] > self._arr["upperbound"]):
            raise ValueError(
                "Lower bound must be <= upper bound for all intervals."
            )

    @property
    def shape(self) -> Tuple[int, ...]:
        return self._arr.shape

    @property
    def ndim(self) -> int:
        return self._arr.ndim

    @property
    def lowerbound(self) -> np.ndarray:
        return self._arr["lowerbound"]

    @property
    def upperbound(self) -> np.ndarray:
        return self._arr["upperbound"]

    def __getitem__(self, idx):
        return self._arr[idx]

    def __setitem__(self, idx, value):
        self._arr[idx] = value

    def __repr__(self) -> str:
        return f"ArrayInterval(shape={self.shape}, dtype={self._arr.dtype})"

    # --- Arithmetic ---

    def __add__(
        self, other: Union[ArrayInterval, float, int]
    ) -> ArrayInterval:
        if isinstance(other, (int, float)):
            lb_other = np.full(self.shape, float(other))
            ub_other = lb_other
        else:
            lb_other, ub_other = other.lowerbound, other.upperbound

        with RoundingContext(RoundingMode.DOWNWARD):
            res_lb = self.lowerbound + lb_other
        with RoundingContext(RoundingMode.UPWARD):
            res_ub = self.upperbound + ub_other

        return self._from_bounds(res_lb, res_ub)

    def __sub__(
        self, other: Union[ArrayInterval, float, int]
    ) -> ArrayInterval:
        if isinstance(other, (int, float)):
            lb_other = np.full(self.shape, float(other))
            ub_other = lb_other
        else:
            lb_other, ub_other = other.lowerbound, other.upperbound

        with RoundingContext(RoundingMode.DOWNWARD):
            res_lb = self.lowerbound - ub_other
        with RoundingContext(RoundingMode.UPWARD):
            res_ub = self.upperbound - lb_other

        return self._from_bounds(res_lb, res_ub)

    def __mul__(
        self, other: Union[ArrayInterval, float, int]
    ) -> ArrayInterval:
        if isinstance(other, (int, float)):
            lb_other = np.full(self.shape, float(other))
            ub_other = lb_other
        else:
            lb_other, ub_other = other.lowerbound, other.upperbound

        # Interval multiplication: [min(ac, ad, bc, bd), max(ac, ad, bc, bd)]
        with RoundingContext(RoundingMode.DOWNWARD):
            p1 = self.lowerbound * lb_other
            p2 = self.lowerbound * ub_other
            p3 = self.upperbound * lb_other
            p4 = self.upperbound * ub_other
            res_lb = np.minimum.reduce([p1, p2, p3, p4])

        with RoundingContext(RoundingMode.UPWARD):
            p1 = self.lowerbound * lb_other
            p2 = self.lowerbound * ub_other
            p3 = self.upperbound * lb_other
            p4 = self.upperbound * ub_other
            res_ub = np.maximum.reduce([p1, p2, p3, p4])

        return self._from_bounds(res_lb, res_ub)

    def __matmul__(self, other: ArrayInterval) -> ArrayInterval:
        """
        Rigorous matrix multiplication using vectorized operations.

        For C = A @ B, each element C_ij is the sum of products A_ik * B_kj.
        To ensure outward rounding:
        - Lower bound: Sum of minimum products for each k.
        - Upper bound: Sum of maximum products for each k.
        """
        if self.ndim != 2 or other.ndim != 2:
            raise NotImplementedError(
                "Matmul currently only supported for 2D arrays."
            )

        m, k = self.shape
        _, n = other.shape

        # Expand dimensions for broadcasting:
        # self: (m, k, 1) -> (m, k, n)
        # other: (k, n) -> (1, k, n)
        self_lb = self.lowerbound[:, :, np.newaxis]  # (m, k, 1)
        self_ub = self.upperbound[:, :, np.newaxis]  # (m, k, 1)
        other_lb = other.lowerbound[np.newaxis, :, :]  # (1, k, n)
        other_ub = other.upperbound[np.newaxis, :, :]  # (1, k, n)

        # Compute all four products for each (i, j, k)
        with RoundingContext(RoundingMode.DOWNWARD):
            p1 = self_lb * other_lb
            p2 = self_lb * other_ub
            p3 = self_ub * other_lb
            p4 = self_ub * other_ub

            # Find min product for each (i, j, k)
            min_products = np.minimum.reduce([p1, p2, p3, p4])

            # Sum along k-axis with downward rounding
            res_lb = np.sum(min_products, axis=1)  # (m, n)

        with RoundingContext(RoundingMode.UPWARD):
            p1 = self_lb * other_lb
            p2 = self_lb * other_ub
            p3 = self_ub * other_lb
            p4 = self_ub * other_ub

            # Find max product for each (i, j, k)
            max_products = np.maximum.reduce([p1, p2, p3, p4])

            # Sum along k-axis with upward rounding
            res_ub = np.sum(max_products, axis=1)  # (m, n)

        return self._from_bounds(res_lb, res_ub)

    def _from_bounds(self, lb: np.ndarray, ub: np.ndarray) -> ArrayInterval:
        res = np.empty(lb.shape, dtype=scalar_interval_dtype)
        res["lowerbound"] = lb
        res["upperbound"] = ub
        return ArrayInterval(res)

    @staticmethod
    def from_scalar_intervals(data: np.ndarray) -> ArrayInterval:
        """Converts an object array of ScalarIntervals to ArrayInterval."""
        res = np.empty(data.shape, dtype=scalar_interval_dtype)
        for idx, val in np.ndenumerate(data):
            res[idx] = (val.lowerbound, val.upperbound)
        return ArrayInterval(res)
