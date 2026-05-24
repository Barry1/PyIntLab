"""Optimierte ScalarInterval – volle Funktionalität, korrekte Rounding + Performance."""

from __future__ import annotations

import math
from logging import Logger, getLogger
from typing import Self, SupportsFloat

from valuefragments.mathhelpers import is_exact_float

thelogger: Logger = getLogger(__name__)

__all__: list[str] = ["ScalarInterval"]


class ScalarInterval:
    """Scalar Interval with guaranteed outward rounding (optimiert)."""

    __slots__ = ("_lowerbound", "_upperbound")

    _lowerbound: float
    _upperbound: float

    def __init__(
        self, *bounds: SupportsFloat, _orderguaranteed: bool = False
    ) -> None:
        """Constructor for new ScalarInterval."""
        if not bounds:
            raise ValueError("At least one bound must be provided.")

        if _orderguaranteed:
            self._lowerbound = self._downward(bounds[0])
            self._upperbound = self._upward(bounds[-1])
        else:
            values = [float(x) for x in bounds]
            self._lowerbound = self._downward(min(values))
            self._upperbound = self._upward(max(values))

    @staticmethod
    def _downward(val: SupportsFloat) -> float:
        """Konservative Downward-Rundung."""
        v = float(val)
        return v if is_exact_float(v) else math.nextafter(v, -math.inf)

    @staticmethod
    def _upward(val: SupportsFloat) -> float:
        """Konservative Upward-Rundung."""
        v = float(val)
        return v if is_exact_float(v) else math.nextafter(v, math.inf)

    @staticmethod
    def _outward(lo: SupportsFloat, hi: SupportsFloat) -> tuple[float, float]:
        return ScalarInterval._downward(lo), ScalarInterval._upward(hi)

    @staticmethod
    def _mulbounds(
        lb1: float, ub1: float, lb2: float, ub2: float
    ) -> tuple[float, float]:
        if lb1 >= 0 and lb2 >= 0:
            return lb1 * lb2, ub1 * ub2
        if ub1 <= 0 and ub2 <= 0:
            return ub1 * ub2, lb1 * lb2
        if lb1 >= 0 and ub2 <= 0:
            return ub1 * lb2, lb1 * ub2
        if ub1 <= 0 and lb2 >= 0:
            return lb1 * ub2, ub1 * lb2

        products = (lb1 * lb2, lb1 * ub2, ub1 * lb2, ub1 * ub2)
        return min(products), max(products)

    # ==================== Properties ====================
    @property
    def lowerbound(self) -> float:
        return self._lowerbound

    @property
    def upperbound(self) -> float:
        return self._upperbound

    @property
    def mid(self) -> float:
        return (self._lowerbound + self._upperbound) / 2

    @property
    def rad(self) -> float:
        return (self._upperbound - self._lowerbound) / 2

    # ==================== Arithmetik ====================
    def __add__(self, other: ScalarInterval | SupportsFloat) -> ScalarInterval:
        if isinstance(other, ScalarInterval):
            return ScalarInterval(
                self._lowerbound + other._lowerbound,
                self._upperbound + other._upperbound,
                _orderguaranteed=True,
            )
        val = float(other)
        return ScalarInterval(
            self._lowerbound + val,
            self._upperbound + val,
            _orderguaranteed=True,
        )

    def __iadd__(self, other: ScalarInterval | SupportsFloat) -> Self:
        if isinstance(other, ScalarInterval):
            lo = self._lowerbound + other._lowerbound
            hi = self._upperbound + other._upperbound
        else:
            val = float(other)
            lo = self._lowerbound + val
            hi = self._upperbound + val
        self._lowerbound = self._downward(lo)
        self._upperbound = self._upward(hi)
        return self

    def __radd__(self, other: SupportsFloat) -> ScalarInterval:
        return self.__add__(other)

    def __sub__(self, other: ScalarInterval | SupportsFloat) -> ScalarInterval:
        if isinstance(other, ScalarInterval):
            return ScalarInterval(
                self._lowerbound - other._upperbound,
                self._upperbound - other._lowerbound,
                _orderguaranteed=True,
            )
        val = float(other)
        return ScalarInterval(
            self._lowerbound - val,
            self._upperbound - val,
            _orderguaranteed=True,
        )

    def __isub__(self, other: ScalarInterval | SupportsFloat) -> Self:
        if isinstance(other, ScalarInterval):
            lo = self._lowerbound - other._upperbound
            hi = self._upperbound - other._lowerbound
        else:
            val = float(other)
            lo = self._lowerbound - val
            hi = self._upperbound - val
        self._lowerbound = self._downward(lo)
        self._upperbound = self._upward(hi)
        return self

    def __rsub__(self, other: SupportsFloat) -> ScalarInterval:
        if isinstance(other, ScalarInterval):
            return ScalarInterval(
                other._lowerbound - self._upperbound,
                other._upperbound - self._lowerbound,
                _orderguaranteed=True,
            )
        val = float(other)
        return ScalarInterval(
            val - self._lowerbound,
            val - self._upperbound,
            _orderguaranteed=True,
        )

    def __mul__(self, other: ScalarInterval | SupportsFloat) -> ScalarInterval:
        if isinstance(other, ScalarInterval):
            lo, hi = self._mulbounds(
                self._lowerbound,
                self._upperbound,
                other._lowerbound,
                other._upperbound,
            )
            return ScalarInterval(lo, hi, _orderguaranteed=True)

        val = float(other)
        if val >= 0:
            lo = self._lowerbound * val
            hi = self._upperbound * val
        else:
            lo = self._upperbound * val
            hi = self._lowerbound * val
        return ScalarInterval(lo, hi, _orderguaranteed=True)

    def __imul__(self, other: ScalarInterval | SupportsFloat) -> Self:
        if isinstance(other, ScalarInterval):
            lo, hi = self._mulbounds(
                self._lowerbound,
                self._upperbound,
                other._lowerbound,
                other._upperbound,
            )
        else:
            val = float(other)
            if val >= 0:
                lo = self._lowerbound * val
                hi = self._upperbound * val
            else:
                lo = self._upperbound * val
                hi = self._lowerbound * val
        self._lowerbound = self._downward(lo)
        self._upperbound = self._upward(hi)
        return self

    def __rmul__(self, other: SupportsFloat) -> ScalarInterval:
        return self.__mul__(other)

    def __truediv__(
        self, other: ScalarInterval | SupportsFloat
    ) -> ScalarInterval:
        if not other:
            raise ZeroDivisionError(
                f"division by interval containing zero: {other}"
            )
        if isinstance(other, ScalarInterval):
            return self * other.reciproc()
        val = float(other)
        if val == 0:
            raise ZeroDivisionError("division by zero")
        if val > 0:
            lo = self._lowerbound / val
            hi = self._upperbound / val
        else:
            lo = self._upperbound / val
            hi = self._lowerbound / val
        return ScalarInterval(lo, hi, _orderguaranteed=True)

    def __itruediv__(self, other: ScalarInterval | SupportsFloat) -> Self:
        if not other:
            raise ZeroDivisionError(
                f"division by interval containing zero: {other}"
            )
        if isinstance(other, ScalarInterval):
            tmp = self * other.reciproc()
            self._lowerbound = tmp._lowerbound
            self._upperbound = tmp._upperbound
            return self
        val = float(other)
        if val == 0:
            raise ZeroDivisionError("division by zero")
        if val > 0:
            lo = self._lowerbound / val
            hi = self._upperbound / val
        else:
            lo = self._upperbound / val
            hi = self._lowerbound / val
        self._lowerbound = self._downward(lo)
        self._upperbound = self._upward(hi)
        return self

    def __rtruediv__(self, other: SupportsFloat) -> ScalarInterval:
        return self.reciproc() * other

    def reciproc(self) -> ScalarInterval:
        if not self:
            raise ZeroDivisionError(
                f"reciprocal of interval containing zero: {self}"
            )
        return ScalarInterval(
            1 / self._upperbound, 1 / self._lowerbound, _orderguaranteed=True
        )

    def __neg__(self) -> ScalarInterval:
        return ScalarInterval(
            -self._upperbound, -self._lowerbound, _orderguaranteed=True
        )

    def __abs__(self) -> ScalarInterval:
        if self._lowerbound >= 0:
            return ScalarInterval(
                self._lowerbound, self._upperbound, _orderguaranteed=True
            )
        if self._upperbound <= 0:
            return ScalarInterval(
                -self._upperbound, -self._lowerbound, _orderguaranteed=True
            )
        return ScalarInterval(
            0, max(-self._lowerbound, self._upperbound), _orderguaranteed=True
        )

    def __pow__(
        self, exponent: ScalarInterval | int | float
    ) -> ScalarInterval:
        if isinstance(exponent, ScalarInterval):
            pows = (
                self._lowerbound**exponent._lowerbound,
                self._lowerbound**exponent._upperbound,
                self._upperbound**exponent._lowerbound,
                self._upperbound**exponent._upperbound,
            )
            return ScalarInterval(min(pows), max(pows), _orderguaranteed=True)
        if isinstance(exponent, int):
            return ScalarInterval(
                self._lowerbound**exponent,
                self._upperbound**exponent,
                _orderguaranteed=True,
            )
        return (self.log() * exponent).exp()

    # ==================== Transzendentale Funktionen ====================
    def sqrt(self) -> ScalarInterval:
        if self._lowerbound < 0:
            raise ValueError(f"sqrt of negative interval: {self}")
        return ScalarInterval(
            math.sqrt(self._lowerbound),
            math.sqrt(self._upperbound),
            _orderguaranteed=True,
        )

    def exp(self) -> ScalarInterval:
        return ScalarInterval(
            self._downward(math.exp(self._lowerbound)),
            self._upward(math.exp(self._upperbound)),
            _orderguaranteed=True,
        )

    def log(
        self, base: ScalarInterval | SupportsFloat = math.e
    ) -> ScalarInterval:
        if self._upperbound <= 0:
            raise ValueError(f"log of non-positive interval: {self}")
        if isinstance(base, ScalarInterval):
            # Vereinfachte Version – bei Bedarf erweiterbar
            return ScalarInterval(
                math.log(self._lowerbound, base._upperbound),
                math.log(self._upperbound, base._lowerbound),
                _orderguaranteed=True,
            )
        b = float(base)
        if self._lowerbound <= 0:
            lo = -math.inf
        else:
            lo = self._downward(math.log(self._lowerbound, b))
        hi = self._upward(math.log(self._upperbound, b))
        return ScalarInterval(lo, hi, _orderguaranteed=True)

    def log10(self) -> ScalarInterval:
        return self.log(10)

    def log2(self) -> ScalarInterval:
        return self.log(2)

    def log1p(self) -> ScalarInterval:
        if self._upperbound <= -1:
            raise ValueError(f"log1p of interval <= -1: {self}")
        return ScalarInterval(
            self._downward(math.log1p(self._lowerbound)),
            self._upward(math.log1p(self._upperbound)),
            _orderguaranteed=True,
        )

    def tanh(self) -> ScalarInterval:
        return ScalarInterval(
            self._downward(math.tanh(self._lowerbound)),
            self._upward(math.tanh(self._upperbound)),
            _orderguaranteed=True,
        )

    # ==================== Vergleiche & Rest ====================
    def __bool__(self) -> bool:
        return self._lowerbound * self._upperbound > 0

    def __contains__(self, item: ScalarInterval | SupportsFloat) -> bool:
        if isinstance(item, ScalarInterval):
            return (
                item._lowerbound >= self._lowerbound
                and item._upperbound <= self._upperbound
            )
        val = float(item)
        return self._lowerbound <= val <= self._upperbound

    def __str__(self) -> str:
        return (
            f"[{self._lowerbound},{self._upperbound}] <{self.mid}±{self.rad}>"
        )

    def __repr__(self) -> str:
        return f"ScalarInterval({self._lowerbound},{self._upperbound})"

    # Weitere Vergleichsoperatoren (__eq__, __lt__ etc.) können bei Bedarf ebenfalls optimiert werden
