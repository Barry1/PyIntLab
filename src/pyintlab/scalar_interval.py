"""Bastian is working on interval arithmetics."""

from __future__ import annotations

import math
from logging import Logger, getLogger

from valuefragments.mathhelpers import is_exact_float
from valuefragments.valuetyping import TYPE_CHECKING, Self, SupportsFloat

thelogger: Logger = getLogger(__name__)
if not TYPE_CHECKING:
    try:
        # pylint: disable=redefined-builtin
        from Cython import float
    except ImportError:
        thelogger.info("No cython here. Using python float instead.")

__all__: list[str] = ["ScalarInterval"]


class ScalarInterval:  # inheritance from object could be suppressed
    """Class for scalars with uncertainty."""

    __slots__ = (
        "_lowerbound",
        "_upperbound",
    )
    # measured with from pympler import asizeof by using __slots__ memory
    # usage of one ScalerInterval has been reduced from 504 to 96 bytes.
    # That is less than 20% of the original size.
    _lowerbound: float
    _upperbound: float
    # __new__ is not needed as the default is sufficient

    @property
    def lowerbound(self) -> float:
        """Getter for the lower bound of the interval."""
        return self._lowerbound

    @lowerbound.setter
    def lowerbound(self, value: SupportsFloat) -> None:
        """Setter for the lower bound of the interval."""
        self._lowerbound = ScalarInterval._downward(value)

    @property
    def upperbound(self) -> float:
        """Getter for the upper bound of the interval."""
        return self._upperbound

    @upperbound.setter
    def upperbound(self, value: SupportsFloat) -> None:
        """Setter for the upper  bound of the interval."""
        self._upperbound = ScalarInterval._upward(value)

    def __init__(
        self, *bounds: SupportsFloat, _orderguaranteed: bool = False
    ) -> None:
        """Constructor for new ScalarInterval.

        You can handover any number of (real) arguments, the resulting Interval
        will automatically be the convex hull (from min to max).
        """
        if not bounds:
            raise ValueError("At least one bound must be provided.")
        if _orderguaranteed:
            self.lowerbound = bounds[0]
            self.upperbound = bounds[-1]
        else:
            self.lowerbound = min(bounds)
            self.upperbound = max(bounds)

    @staticmethod
    def _outward(lo: SupportsFloat, hi: SupportsFloat) -> tuple[float, float]:
        """Konservative Outward-Rundung: lo -> -inf, hi -> +inf."""
        return lo if is_exact_float(lo) else math.nextafter(lo, -math.inf), (
            hi if is_exact_float(hi) else math.nextafter(hi, math.inf)
        )

    @staticmethod
    def _upward(val: SupportsFloat) -> float:
        """Konservative Upward-Rundung: -> +inf."""
        return val if is_exact_float(val) else math.nextafter(val, math.inf)

    @staticmethod
    def _downward(val: SupportsFloat) -> float:
        """Konservative Downward-Rundung: -> -inf."""
        return val if is_exact_float(val) else math.nextafter(val, -math.inf)

    @property
    def mid(self) -> float:
        """Midpoint of interval."""
        return (self.lowerbound + self.upperbound) / 2

    @property
    def rad(self) -> float:
        """Radius of interval."""
        return (self.upperbound - self.lowerbound) / 2

    # <https://www.tutorialsteacher.com/python/magic-methods-in-python>
    # <https://rszalski.github.io/magicmethods/>

    def __abs__(self) -> ScalarInterval:
        """Absolute value of the Interval.

        Open thought: The absInterval is the Interval containing
        all abs values from all elements of the given Interval.
        """
        return (
            ScalarInterval(abs(self.lowerbound), abs(self.upperbound))
            if self
            else ScalarInterval(
                0,
                max(-self.lowerbound, self.upperbound),
                _orderguaranteed=True,
            )
        )

    def __str__(self) -> str:
        """Show a readable representation of the Interval."""
        return f"[{self.lowerbound},{self.upperbound}] <{self.mid}±{self.rad}>"

    def __repr__(self) -> str:
        """Show a representation of the Interval for reconstruction."""
        return f"ScalarInterval({self.lowerbound},{self.upperbound})"

    def __ge__(self, other: ScalarInterval | SupportsFloat) -> bool:
        """Dunder method for greater equals."""
        return (
            self.lowerbound >= other.upperbound
            if isinstance(other, ScalarInterval)
            else self.lowerbound >= float(other)
        )

    def __gt__(self, other: ScalarInterval | SupportsFloat) -> bool:
        """Dunder method for greater than."""
        return (
            self.lowerbound > other.upperbound
            if isinstance(other, ScalarInterval)
            else self.lowerbound > float(other)
        )

    def __le__(self, other: ScalarInterval | SupportsFloat) -> bool:
        """Dunder method for less equals."""
        return (
            self.upperbound <= other.lowerbound
            if isinstance(other, ScalarInterval)
            else self.upperbound <= float(other)
        )

    def __lt__(self, other: ScalarInterval | SupportsFloat) -> bool:
        """Dunder method for less than."""
        return (
            self.upperbound < other.lowerbound
            if isinstance(other, ScalarInterval)
            else self.upperbound < float(other)
        )

    def __eq__(self, other: object) -> bool:
        """Dunder method for checking identity."""
        return (
            (
                self.lowerbound == other.lowerbound
                and self.upperbound == other.upperbound
            )
            if isinstance(other, ScalarInterval)
            else NotImplemented
        )

    def __add__(self, other: ScalarInterval | SupportsFloat) -> ScalarInterval:
        """Dunder method for addition."""
        return (
            ScalarInterval(
                self.lowerbound + other.lowerbound,
                self.upperbound + other.upperbound,
                _orderguaranteed=True,
            )
            if isinstance(other, ScalarInterval)
            else ScalarInterval(
                self.lowerbound + float(other),
                self.upperbound + float(other),
                _orderguaranteed=True,
            )
        )

    def __iadd__(self, other: ScalarInterval | SupportsFloat) -> Self:
        """Dunder method for inplace addition."""
        if isinstance(other, ScalarInterval):
            self.lowerbound += other.lowerbound
            self.upperbound += other.upperbound
            return self
        _val: float = float(other)
        self.lowerbound += _val
        self.upperbound += _val
        return self

    def __radd__(self, other: ScalarInterval | float) -> ScalarInterval:
        """Dunder method for right addition."""
        if isinstance(other, ScalarInterval):
            return ScalarInterval(
                self.lowerbound + other.lowerbound,
                self.upperbound + other.upperbound,
            )
        return ScalarInterval(self.lowerbound + other, self.upperbound + other)

    def reciproc(self) -> ScalarInterval:
        """Build 1/x for ScalarInterval x."""
        if not self:  # calls __bool__ method
            raise ZeroDivisionError(
                f"Can not build the reziprocal of indefinite Interval {self}."
            )
        return ScalarInterval(1 / self.upperbound, 1 / self.lowerbound)

    @staticmethod
    def _mulbounds(
        lb1: float, ub1: float, lb2: float, ub2: float
    ) -> tuple[float, float]:
        if lb1 >= 0 and lb2 >= 0:
            return lb1 * lb2, ub1 * ub2
        if ub1 <= 0 and ub2 <= 0:
            return ub1 * ub2, lb1 * lb2
        products: tuple[float, float, float, float] = (
            lb1 * lb2,
            lb1 * ub2,
            ub1 * lb2,
            ub1 * ub2,
        )
        return min(products), max(products)

    def __mul__(self, other: ScalarInterval | SupportsFloat) -> ScalarInterval:
        """Dunder method for (left) multiplication."""
        if isinstance(other, ScalarInterval):
            return ScalarInterval(
                *ScalarInterval._mulbounds(
                    self.lowerbound,
                    self.upperbound,
                    other.lowerbound,
                    other.upperbound,
                ),
                _orderguaranteed=True,
            )
        _val: float = float(other)
        return ScalarInterval(self.lowerbound * _val, self.upperbound * _val)

    def __imul__(self, other: ScalarInterval | SupportsFloat) -> Self:
        """Dunder method for (left) inplace multiplication."""
        if isinstance(other, ScalarInterval):
            self.lowerbound, self.upperbound = ScalarInterval._mulbounds(
                self.lowerbound,
                self.upperbound,
                other.lowerbound,
                other.upperbound,
            )
        else:
            _val: float = float(other)
            self.lowerbound *= _val
            self.upperbound *= _val
            if _val < 0:
                self.lowerbound, self.upperbound = (
                    self.upperbound,
                    self.lowerbound,
                )
        return self

    def __pos__(self) -> ScalarInterval:
        """Dunder method for positive."""
        return self

    def __ne__(self, other: object) -> bool:
        """Dunder method for checking non-identity."""
        return not self.__eq__(other)

    def __neg__(self) -> ScalarInterval:
        """Switches the sign of ScalarInterval x ==> -x."""
        return ScalarInterval(
            -self.upperbound, -self.lowerbound, _orderguaranteed=True
        )

    def __rmul__(
        self, other: ScalarInterval | SupportsFloat
    ) -> ScalarInterval:
        """Dunder method for right multiplikation."""
        if isinstance(other, ScalarInterval):
            return ScalarInterval(
                *ScalarInterval._mulbounds(
                    other.lowerbound,
                    other.upperbound,
                    self.lowerbound,
                    self.upperbound,
                ),
                _orderguaranteed=True,
            )
        _val: float = float(other)
        return ScalarInterval(_val * self.lowerbound, _val * self.upperbound)

    def __bool__(self) -> bool:  # python3
        """Dunder method for definiteness (does not contain zero)."""
        return self.lowerbound * self.upperbound > 0

    def __sub__(self, other: ScalarInterval | SupportsFloat) -> ScalarInterval:
        """Dunder method for subtraction."""
        if isinstance(other, ScalarInterval):
            return ScalarInterval(
                self.lowerbound - other.upperbound,
                self.upperbound - other.lowerbound,
                _orderguaranteed=True,
            )
        _val: float = float(other)
        return ScalarInterval(
            self.lowerbound - _val,
            self.upperbound - _val,
            _orderguaranteed=True,
        )

    def __isub__(self, other: ScalarInterval | SupportsFloat) -> Self:
        """Dunder method for inplace subtraction."""
        if isinstance(other, ScalarInterval):
            self.lowerbound -= other.upperbound
            self.upperbound -= other.lowerbound
            return self
        _val: float = float(other)
        self.lowerbound -= _val
        self.upperbound -= _val
        return self

    def __rsub__(
        self, other: ScalarInterval | SupportsFloat
    ) -> ScalarInterval:
        """Dunder method for rightsubtraction."""
        if isinstance(other, ScalarInterval):
            return ScalarInterval(
                other.lowerbound - self.upperbound,
                other.upperbound - self.lowerbound,
            )
        _val: float = float(other)
        return ScalarInterval(_val - self.lowerbound, _val - self.upperbound)

    def __truediv__(
        self, other: ScalarInterval | SupportsFloat
    ) -> ScalarInterval:
        """Dunder method for (left) true division."""
        if not other:
            raise ZeroDivisionError(
                f"Can not divide by indefinite Interval {other}."
            )
        if isinstance(other, ScalarInterval):
            return self.__mul__(other.reciproc())
        _val: float = float(other)
        return ScalarInterval(self.lowerbound / _val, self.upperbound / _val)

    def __itruediv__(
        self, other: ScalarInterval | SupportsFloat
    ) -> Self:
        """Dunder method for (left) true inplace division."""
        if not other:
            raise ZeroDivisionError(
                f"Can not divide by indefinite Interval {other}."
            )
        if isinstance(other, ScalarInterval):
            return self.__imul__(other.reciproc())
        _val: float = float(other)
        self.lowerbound /= _val
        self.upperbound /= _val
        return self

    # https://docs.python.org/3.6/reference/datamodel.html#object.__radd__
    def __rtruediv__(self, other: float) -> ScalarInterval:
        """Dunder method for right true division."""
        return self.reciproc() * other

    def __contains__(self, item: ScalarInterval | SupportsFloat) -> bool:
        """Return boolean indicator if item is within interval."""
        if isinstance(item, ScalarInterval):
            return (
                item.lowerbound >= self.lowerbound
                and item.upperbound <= self.upperbound
            )
        return self.lowerbound <= float(item) <= self.upperbound

    def __pow__(
        self, exponent: ScalarInterval | int | float
    ) -> ScalarInterval:
        """Return the interval to the power of the given exponent."""
        if isinstance(exponent, ScalarInterval):
            pows: tuple[float, float, float, float] = (
                self.lowerbound**exponent.lowerbound,
                self.lowerbound**exponent.upperbound,
                self.upperbound**exponent.lowerbound,
                self.upperbound**exponent.upperbound,
            )
            return ScalarInterval(min(pows), max(pows), _orderguaranteed=True)
        if isinstance(exponent, int):
            return ScalarInterval(
                self.lowerbound**exponent, self.upperbound**exponent
            )
        return (self.log() * exponent).exp()

    ###########################################################################
    # following are implementations of monoton increasing functions
    ###########################################################################
    def sqrt(self) -> ScalarInterval:
        """Return the square root of the interval."""
        return ScalarInterval(
            math.sqrt(self.lowerbound), math.sqrt(self.upperbound)
        )

    def log10(self) -> ScalarInterval:
        """Return the base 10 logarithm of the interval."""
        return ScalarInterval(
            math.log10(self.lowerbound), math.log10(self.upperbound)
        )

    def log1p(self) -> ScalarInterval:
        """Return the natural logarithm of 1+x."""
        return ScalarInterval(
            math.log1p(self.lowerbound), math.log1p(self.upperbound)
        )

    def log2(self) -> ScalarInterval:
        """Return the base 2 logarithm of the interval."""
        return ScalarInterval(
            math.log2(self.lowerbound), math.log2(self.upperbound)
        )

    def exp(self) -> ScalarInterval:
        """Return e to the power of the interval."""
        return ScalarInterval(
            math.exp(self.lowerbound), math.exp(self.upperbound)
        )

    def log(
        self, base: ScalarInterval | SupportsFloat = math.e
    ) -> ScalarInterval:
        """Return the logarithm to the given base or natural if omitted."""
        if isinstance(base, ScalarInterval):
            return ScalarInterval(
                math.log(self.lowerbound, base.upperbound),
                math.log(self.upperbound, base.lowerbound),
            )
        return ScalarInterval(
            math.log(self.lowerbound, base), math.log(self.upperbound, base)
        )

    def tanh(self) -> ScalarInterval:
        """Return the hyperbolic tangens of the interval."""
        return ScalarInterval(
            math.tanh(self.lowerbound), math.tanh(self.upperbound)
        )


###############################################################################
if __name__ == "__main__":  # Small application
    pitest: ScalarInterval = ScalarInterval(3, 4)
    rtest: ScalarInterval = ScalarInterval(2.2, 2.4)
    print("========== INPUT ==========")
    print(f"pi {pitest}")
    print(f"radius {rtest}")
    print("========== OUTPUT ==========")
    print(f"diameter {rtest + rtest}")
    print(f"area {rtest * rtest * pitest}")
    print(f"volume {4 / 3 * rtest * rtest * rtest * pitest}")
