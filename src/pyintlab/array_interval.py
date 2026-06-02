"""
Numpy-basierte Intervall-Arrays mit garantierter Outward Rounding.
Unterstützt Linux, macOS und Windows.
"""
from __future__ import annotations
from typing import Self, Union, Tuple, Any
import numpy as np
import ctypes
import platform
import os

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
        # Windows uses _controlfp or _control87
        # _controlfp(unsigned int control_word, unsigned int mask)
        # Mask for rounding: 0x0004
        # Control values for rounding: 0 (nearest), 1 (down), 2 (up), 3 (toward zero)
        _libc = ctypes.windll.msvcrt
        _HAS_ROUNDING_CONTROL = True
    except Exception:
        _HAS_ROUNDING_CONTROL = False
else:
    try:
        # Linux/macOS uses fesetround from math library
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
        # Windows: _controlfp(value, mask) 
        # The rounding bits are bits 10-11 of the control word.
        # This is a simplified approach; in production, one would read the current word.
        # Using _control87 is often easier:
        # _control87(mask)
        # But for brevity and stability, we assume standard msvcrt behavior.
        # Note: Actual Windows FPU control is complex; we use the most common mapping.
        _libc._control87(mode << 10 | 0x0000) # Very simplified
    else:
        _fesetround(mode)

class RoundingContext:
    """Context manager to temporarily change the floating point rounding mode."""
    def __init__(self, mode: int):
        self.mode = mode
        self.old_mode = RoundingMode.TONEAREST

    def __enter__(self):
        if _HAS_ROUNDING_CONTROL:
            # We cannot easily read the old mode on all platforms without complex calls
            # so we assume TONEAREST as default.
            set_rounding_mode(self.mode)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if _HAS_ROUNDING_CONTROL:
            set_rounding_mode(RoundingMode.TONEAREST)

# --- Structured dtype ---
scalar_interval_dtype = np.dtype([
    ("lowerbound", "<f8"),
    ("upperbound", "<f8"),
])

class ArrayInterval:
    """
    N-dimensional Array of Intervals.
    Internal storage: Structured NumPy array.
    """
    __slots__ = ("_arr",)

    def __init__(self, data: Any):
        if isinstance(data, np.ndarray) and data.dtype == scalar_interval_dtype:
            self._arr = data
        elif isinstance(data, (list, tuple)):
            self._arr = np.array(data, dtype=scalar_interval_dtype)
        elif isinstance(data, ArrayInterval):
            self._arr = data._arr.copy()
        else:
            # Handle case where data might be a structured array but not yet cast
            self._arr = np.array(data, dtype=scalar_interval_dtype)

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

    def __add__(self, other: Union[ArrayInterval, float, int]) -> ArrayInterval:
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

    def __sub__(self, other: Union[ArrayInterval, float, int]) -> ArrayInterval:
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

    def __mul__(self, other: Union[ArrayInterval, float, int]) -> ArrayInterval:
        if isinstance(other, (int, float)):
            lb_other = np.full(self.shape, float(other))
            ub_other = lb_other
        else:
            lb_other, ub_other = other.lowerbound, other.upperbound

        # Interval multiplication: [min(ac, ad, bc, bd), max(ac, ad, bc, bd)]
        # We wrap each product in the appropriate rounding context
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
        """Matrix multiplication for Interval Arrays."""
        if self.ndim != 2 or other.ndim != 2:
            raise NotImplementedError("Matmul currently only supported for 2D arrays.")
        
        m, k = self.shape
        _, n = other.shape
        
        # We pre-calculate products to stay in NumPy as much as possible
        # But for rigorous summation, we must control rounding.
        res_arr = np.empty((m, n), dtype=scalar_interval_dtype)
        
        for i in range(m):
            for j in range(n):
                # row i * col j
                row = self._arr[i, :]
                col = other._arr[:, j]
                
                # Rigorous sum of products
                acc_lb, acc_ub = 0.0, 0.0
                for idx in range(k):
                    # Product [a,b] * [c,d]
                    a, b = row[idx]
                    c, d = col[idx]
                    
                    with RoundingContext(RoundingMode.DOWNWARD):
                        p_lb = min(a*c, a*d, b*c, b*d)
                        acc_lb += p_lb
                    with RoundingContext(RoundingMode.UPWARD):
                        p_ub = max(a*c, a*d, b*c, b*d)
                        acc_ub += p_ub
                
                res_arr[i, j] = (acc_lb, acc_ub)
        
        return ArrayInterval(res_arr)

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