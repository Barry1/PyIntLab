"""Bastian is working on interval arithmetics."""

from __future__ import annotations

import math
from logging import Logger, getLogger
from typing import TYPE_CHECKING, Literal, SupportsFloat

thelogger: Logger = getLogger(__name__)
if not TYPE_CHECKING:
    try:
        from Cython import float
    except ImportError:
        thelogger.info("No cython here. Using python float instead.")

__all__: list[str] = []


class ScalarInterval:  # inheritance from object could be suppressed
    """Class for scalars with uncertainty."""

    __slots__: tuple[Literal["lowerbound"], Literal["upperbound"]] = (
        "lowerbound",
        "upperbound",
    )
    # measured with from pympler import asizeof by using __slots__ memory
    # usage of one ScalerInterval has been reduced from 504 to 96 bytes.
    # That is less than 20% of the original size.
    lowerbound: float
    upperbound: float
    # __new__ is not needed as the default is sufficient

    def __init__(self, *bounds: float) -> None:
        """Construct for new ScalarInterval.

        You can handover any number of (real) arguments, the resulting Interval
        will automatically be the convex hull (from min to max).
        """
        if not bounds:
            raise ValueError("At least one bound must be provided.")
        self.lowerbound = min(bounds)
        self.upperbound = max(bounds)

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

    def __str__(self) -> str:
        """Show a readable representation of the Interval."""
        return f"[{self.lowerbound},{self.upperbound}] <{self.mid}±{self.rad}>"

    def __repr__(self) -> str:
        """Show a representation of the Interval for reconstruction."""
        return f"ScalarInterval({self.lowerbound},{self.upperbound})"

    def __ge__(self, other: ScalarInterval | SupportsFloat) -> bool:
        """Dunder method for greater equals."""
        if isinstance(other, ScalarInterval):
            return self.lowerbound >= other.upperbound
        return self.lowerbound >= float(other)

    def __gt__(self, other: ScalarInterval | SupportsFloat) -> bool:
        """Dunder method for greater than."""
        if isinstance(other, ScalarInterval):
            return self.lowerbound > other.upperbound
        return self.lowerbound > float(other)

    def __le__(self, other: ScalarInterval | SupportsFloat) -> bool:
        """Dunder method for less equals."""
        if isinstance(other, ScalarInterval):
            return self.upperbound <= other.lowerbound
        return self.upperbound <= float(other)

    def __lt__(self, other: ScalarInterval | SupportsFloat) -> bool:
        """Dunder method for less than."""
        if isinstance(other, ScalarInterval):
            return self.upperbound < other.lowerbound
        return self.upperbound < float(other)

    def __eq__(self, other: object) -> bool:
        """Dunder method for checking identity."""
        if isinstance(other, ScalarInterval):
            return (
                self.lowerbound == other.lowerbound
                and self.upperbound == other.upperbound
            )
        return NotImplemented

    def __add__(self, other: ScalarInterval | SupportsFloat) -> ScalarInterval:
        """Dunder method for addition."""
        if isinstance(other, ScalarInterval):
            return ScalarInterval(
                self.lowerbound + other.lowerbound,
                self.upperbound + other.upperbound,
            )
        return ScalarInterval(
            self.lowerbound + float(other), self.upperbound + float(other)
        )

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
        if self:  # calls __bool__ method
            return ScalarInterval(1 / self.upperbound, 1 / self.lowerbound)
        raise ZeroDivisionError(
            f"Can not build the reziprocal of indefinite Interval {self}."
        )

    def __mul__(self, other: ScalarInterval | SupportsFloat) -> ScalarInterval:
        """Dunder method for (left) multiplication."""
        if isinstance(other, ScalarInterval):
            return ScalarInterval(
                self.lowerbound * other.lowerbound,
                self.lowerbound * other.upperbound,
                self.upperbound * other.lowerbound,
                self.upperbound * other.upperbound,
            )
        return ScalarInterval(
            self.lowerbound * float(other), self.upperbound * float(other)
        )

    def __neg__(self) -> ScalarInterval:
        """Switches the sign of ScalarInterval x ==> -x."""
        return ScalarInterval(-self.upperbound, -self.lowerbound)

    def __rmul__(self, other: ScalarInterval | SupportsFloat) -> ScalarInterval:
        """Dunder method for right multiplikation."""
        if isinstance(other, ScalarInterval):
            return ScalarInterval(
                other.lowerbound * self.lowerbound,
                other.lowerbound * self.upperbound,
                other.upperbound * self.lowerbound,
                other.upperbound * self.upperbound,
            )
        return ScalarInterval(
            float(other) * self.lowerbound, float(other) * self.upperbound
        )

    def __bool__(self) -> bool:  # python3
        """Dunder method for definiteness (does not contain zero)."""
        return self.lowerbound * self.upperbound > 0

    def __sub__(self, other: ScalarInterval | SupportsFloat) -> ScalarInterval:
        """Dunder method for subtraction."""
        if isinstance(other, ScalarInterval):
            return ScalarInterval(
                self.lowerbound - other.upperbound,
                self.upperbound - other.lowerbound,
            )
        return ScalarInterval(
            self.lowerbound - float(other), self.upperbound - float(other)
        )

    def __rsub__(self, other: ScalarInterval | SupportsFloat) -> ScalarInterval:
        """Dunder method for rightsubtraction."""
        if isinstance(other, ScalarInterval):
            return ScalarInterval(
                other.lowerbound - self.upperbound,
                other.upperbound - self.lowerbound,
            )
        return ScalarInterval(
            float(other) - self.lowerbound, float(other) - self.upperbound
        )

    def __truediv__(self, other: ScalarInterval | SupportsFloat) -> ScalarInterval:
        """Dunder method for (left) true division."""
        if isinstance(other, ScalarInterval):
            return self.__mul__(other.reciproc())
        return ScalarInterval(
            self.lowerbound / float(other), self.upperbound / float(other)
        )

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

    ###########################################################################
    # following are implementations of monoton increasing functions
    ###########################################################################
    def sqrt(self) -> ScalarInterval:
        """Return the square root of the interval."""
        return ScalarInterval(math.sqrt(self.lowerbound), math.sqrt(self.upperbound))

    def log10(self) -> ScalarInterval:
        """Return the base 10 logarithm of the interval."""
        return ScalarInterval(math.log10(self.lowerbound), math.log10(self.upperbound))

    def log1p(self) -> ScalarInterval:
        """Return the natural logarithm of 1+x."""
        return ScalarInterval(math.log1p(self.lowerbound), math.log1p(self.upperbound))

    def log2(self) -> ScalarInterval:
        """Return the base 2 logarithm of the interval."""
        return ScalarInterval(math.log2(self.lowerbound), math.log2(self.upperbound))

    def exp(self) -> ScalarInterval:
        """Return e to the power of the interval."""
        return ScalarInterval(math.exp(self.lowerbound), math.exp(self.upperbound))

    def log(self, base: ScalarInterval | SupportsFloat = math.e) -> ScalarInterval:
        """Return the logarithm to the given base or natural if omitted."""
        if isinstance(base, ScalarInterval):
            return ScalarInterval(
                math.log(self.lowerbound, base.upperbound),
                math.log(self.upperbound, base.lowerbound),
            )
        return ScalarInterval(
            math.log(self.lowerbound, base), math.log(self.upperbound, base)
        )

    def __pow__(self, exponent: ScalarInterval | int | float) -> ScalarInterval:
        """Return the interval to the power of the given exponent."""
        if isinstance(exponent, ScalarInterval):
            return ScalarInterval(
                self.lowerbound**exponent.lowerbound,
                self.lowerbound**exponent.upperbound,
                self.upperbound**exponent.lowerbound,
                self.upperbound**exponent.upperbound,
            )
        if isinstance(exponent, int):
            return ScalarInterval(self.lowerbound**exponent, self.upperbound**exponent)
        return (self.log() * exponent).exp()

    def tanh(self) -> ScalarInterval:
        """Return the hyperbolic tangens of the interval."""
        return ScalarInterval(math.tanh(self.lowerbound), math.tanh(self.upperbound))


__all__.append("ScalarInterval")

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
