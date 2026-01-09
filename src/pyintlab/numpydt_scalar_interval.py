"""Bastian is working on interval arithmetics."""

from __future__ import annotations

import math
from logging import INFO, Logger, basicConfig, getLogger
from typing import TYPE_CHECKING, Self, SupportsFloat

import numpy

thelogger: Logger = getLogger(__name__)
if not TYPE_CHECKING:
    try:
        # pylint: disable=redefined-builtin
        from Cython import float
    except ImportError:
        thelogger.info("No cython here. Using python float instead.")
scalar_interval_dtype: numpy.dtype[numpy.void] = numpy.dtype(
    [("lowerbound", "<f8"), ("upperbound", "<f8")]
)
__all__: list[str] = []


class NPScalarInterval:  # inheritance from object could be suppressed
    """Class for scalars with uncertainty."""

    __slots__: tuple[str] = ("data",)
    data: numpy.void
    # __new__ is not needed as the default is sufficient

    def __init__(self, *bounds: float, orderguaranteed: bool = False) -> None:
        """Construct for new NPScalarInterval.

        You can handover any number of (real) arguments, the resulting Interval
        will automatically be the convex hull (from min to max).
        """
        thelogger.info("__init__ Creating new Interval from bounds: %s", bounds)
        if not bounds:
            raise ValueError("At least one bound must be provided.")
        self.data = (
            numpy.void((bounds[0], bounds[-1]), dtype=scalar_interval_dtype)
            if orderguaranteed
            else numpy.void((min(bounds), max(bounds)), dtype=scalar_interval_dtype)
        )
        print(str(self))
        print(self)
        print(self.data)
        thelogger.info(
            "New Interval %s needing approx. %i Bytes of memory.",
            self,
            self.__sizeof__() + self.data.__sizeof__(),
        )

    @property
    def lowerbound(self) -> float:
        """Lower bound of interval."""
        return self.data["lowerbound"]

    @property
    def upperbound(self) -> float:
        """Upper bound of interval."""
        return self.data["upperbound"]

    @property
    def mid(self) -> float:
        """Midpoint of interval."""
        return (self.data["lowerbound"] + self.data["upperbound"]) / 2

    @property
    def rad(self) -> float:
        """Radius of interval."""
        return (self.data["upperbound"] - self.data["lowerbound"]) / 2

    def __str__(self) -> str:
        """Show a readable representation of the Interval."""
        return f"[{self.data['lowerbound']},{self.data['upperbound']}] <{self.mid}±{self.rad}>"

    def __repr__(self) -> str:
        """Show a representation of the Interval for reconstruction."""
        return f"ScalarInterval({self.data['lowerbound']},{self.data['upperbound']})"

    def __abs__(self) -> NPScalarInterval:
        """Absolute value of the Interval.

        Open thought: The absInterval is the Interval containing
        all abs values from all elements of the given Interval.
        """
        if self:
            # meaning self does not contain 0
            return NPScalarInterval(
                abs(self.data["lowerbound"]), abs(self.data["upperbound"])
            )
        else:
            return NPScalarInterval(
                0,
                max(abs(self.data["lowerbound"]), self.data["upperbound"]),
                orderguaranteed=True,
            )

    def __ge__(self, other: Self | SupportsFloat) -> bool:
        """Dunder method for greater equals."""
        if isinstance(other, NPScalarInterval):
            return self.data["lowerbound"] >= other.data["upperbound"]
        return self.data["lowerbound"] >= float(other)

    def __gt__(self, other: Self | SupportsFloat) -> bool:
        """Dunder method for greater than."""
        if isinstance(other, NPScalarInterval):
            return self.data["lowerbound"] > other.data["upperbound"]
        return self.data["lowerbound"] > float(other)

    def __le__(self, other: Self | SupportsFloat) -> bool:
        """Dunder method for less equals."""
        if isinstance(other, NPScalarInterval):
            return self.data["upperbound"] <= other.data["lowerbound"]
        return self.data["upperbound"] <= float(other)

    def __lt__(self, other: Self | SupportsFloat) -> bool:
        """Dunder method for less than."""
        if isinstance(other, NPScalarInterval):
            return self.data["upperbound"] < other.data["lowerbound"]
        return self.data["upperbound"] < float(other)

    def __eq__(self, other: object) -> bool:
        """Dunder method for checking identity."""
        if isinstance(other, NPScalarInterval):
            return (
                self.data["lowerbound"] == other.data["lowerbound"]
                and self.data["upperbound"] == other.data["upperbound"]
            )
        return NotImplemented

    def __add__(self, other: Self | SupportsFloat) -> NPScalarInterval:
        """Dunder method for addition."""
        if isinstance(other, NPScalarInterval):
            return NPScalarInterval(
                self.data["lowerbound"] + other.data["lowerbound"],
                self.data["upperbound"] + other.data["upperbound"],
                orderguaranteed=True,
            )
        return NPScalarInterval(
            self.data["lowerbound"] + float(other),
            self.data["upperbound"] + float(other),
            orderguaranteed=True,
        )

    def __iadd__(self, other: Self | SupportsFloat) -> Self:
        """Dunder method for inplace addition."""
        if isinstance(other, NPScalarInterval):
            self.data["lowerbound"] += other.data["lowerbound"]
            self.data["upperbound"] += other.data["upperbound"]
            return self
        self.data["lowerbound"] += float(other)
        self.data["upperbound"] += float(other)
        return self

    def __radd__(self, other: Self | float) -> NPScalarInterval:
        """Dunder method for right addition."""
        if isinstance(other, NPScalarInterval):
            return NPScalarInterval(
                self.data["lowerbound"] + other.data["lowerbound"],
                self.data["upperbound"] + other.data["upperbound"],
            )
        return NPScalarInterval(
            self.data["lowerbound"] + other,
            self.data["upperbound"] + other,
        )

    def reciproc(self) -> NPScalarInterval:
        """Build 1/x for NPScalarInterval x."""
        if self:  # calls __bool__ method
            return NPScalarInterval(
                1 / self.data["upperbound"], 1 / self.data["lowerbound"]
            )
        raise ZeroDivisionError(
            f"Can not build the reziprocal of indefinite Interval {self}."
        )

    def __mul__(self, other: Self | SupportsFloat) -> NPScalarInterval:
        """Dunder method for (left) multiplication."""
        if isinstance(other, NPScalarInterval):
            products: tuple[float, float, float, float] = (
                self.data["lowerbound"] * other.data["lowerbound"],
                self.data["lowerbound"] * other.data["upperbound"],
                self.data["upperbound"] * other.data["lowerbound"],
                self.data["upperbound"] * other.data["upperbound"],
            )
            return NPScalarInterval(min(products), max(products), orderguaranteed=True)
        return NPScalarInterval(
            self.data["lowerbound"] * float(other),
            self.data["upperbound"] * float(other),
        )

    def __neg__(self) -> NPScalarInterval:
        """Switches the sign of NPScalarInterval x ==> -x."""
        return NPScalarInterval(
            -self.data["upperbound"],
            -self.data["lowerbound"],
            orderguaranteed=True,
        )

    def __rmul__(self, other: Self | SupportsFloat) -> NPScalarInterval:
        """Dunder method for right multiplikation."""
        if isinstance(other, NPScalarInterval):
            return NPScalarInterval(
                other.data["lowerbound"] * self.data["lowerbound"],
                other.data["lowerbound"] * self.data["upperbound"],
                other.data["upperbound"] * self.data["lowerbound"],
                other.data["upperbound"] * self.data["upperbound"],
            )
        return NPScalarInterval(
            float(other) * self.data["lowerbound"],
            float(other) * self.data["upperbound"],
        )

    def __bool__(self) -> bool:  # python3
        """Dunder method for definiteness (does not contain zero)."""
        return self.data["lowerbound"] * self.data["upperbound"] > 0

    def __sub__(self, other: Self | SupportsFloat) -> NPScalarInterval:
        """Dunder method for subtraction."""
        if isinstance(other, NPScalarInterval):
            return NPScalarInterval(
                self.data["lowerbound"] - other.data["upperbound"],
                self.data["upperbound"] - other.data["lowerbound"],
                orderguaranteed=True,
            )
        return NPScalarInterval(
            self.data["lowerbound"] - float(other),
            self.data["upperbound"] - float(other),
            orderguaranteed=True,
        )

    def __isub__(self, other: Self | SupportsFloat) -> Self:
        """Dunder method for inplace subtraction."""
        if isinstance(other, NPScalarInterval):

            self.data["lowerbound"] -= other.data["upperbound"]
            self.data["upperbound"] -= other.data["lowerbound"]
            return self
        self.data["lowerbound"] -= float(other)
        self.data["upperbound"] -= float(other)
        return self

    def __rsub__(self, other: Self | SupportsFloat) -> NPScalarInterval:
        """Dunder method for rightsubtraction."""
        if isinstance(other, NPScalarInterval):
            return NPScalarInterval(
                other.data["lowerbound"] - self.data["upperbound"],
                other.data["upperbound"] - self.data["lowerbound"],
            )
        return NPScalarInterval(
            float(other) - self.data["lowerbound"],
            float(other) - self.data["upperbound"],
        )

    def __truediv__(self, other: Self | SupportsFloat) -> NPScalarInterval:
        """Dunder method for (left) true division."""
        if isinstance(other, NPScalarInterval):
            return self.__mul__(other.reciproc())
        return NPScalarInterval(
            self.data["lowerbound"] / float(other),
            self.data["upperbound"] / float(other),
        )

    # https://docs.python.org/3.6/reference/datamodel.html#object.__radd__
    def __rtruediv__(self, other: float) -> NPScalarInterval:
        """Dunder method for right true division."""
        return self.reciproc() * other

    def __contains__(self, item: Self | SupportsFloat) -> bool:
        """Return boolean indicator if item is within interval."""
        if isinstance(item, NPScalarInterval):
            return (
                item.data["lowerbound"] >= self.data["lowerbound"]
                and item.data["upperbound"] <= self.data["upperbound"]
            )
        return self.data["lowerbound"] <= float(item) <= self.data["upperbound"]

    ###########################################################################
    # following are implementations of monoton increasing functions
    ###########################################################################
    def sqrt(self) -> NPScalarInterval:
        """Return the square root of the interval."""
        return NPScalarInterval(
            math.sqrt(self.data["lowerbound"]), math.sqrt(self.data["upperbound"])
        )

    def log10(self) -> NPScalarInterval:
        """Return the base 10 logarithm of the interval."""
        return NPScalarInterval(
            math.log10(self.data["lowerbound"]), math.log10(self.data["upperbound"])
        )

    def log1p(self) -> NPScalarInterval:
        """Return the natural logarithm of 1+x."""
        return NPScalarInterval(
            math.log1p(self.data["lowerbound"]), math.log1p(self.data["upperbound"])
        )

    def log2(self) -> NPScalarInterval:
        """Return the base 2 logarithm of the interval."""
        return NPScalarInterval(
            math.log2(self.data["lowerbound"]), math.log2(self.data["upperbound"])
        )

    def exp(self) -> NPScalarInterval:
        """Return e to the power of the interval."""
        return NPScalarInterval(
            math.exp(self.data["lowerbound"]), math.exp(self.data["upperbound"])
        )

    def log(self, base: Self | SupportsFloat = math.e) -> NPScalarInterval:
        """Return the logarithm to the given base or natural if omitted."""
        if isinstance(base, NPScalarInterval):
            return NPScalarInterval(
                math.log(self.data["lowerbound"], base.data["upperbound"]),
                math.log(self.data["upperbound"], base.data["lowerbound"]),
            )
        return NPScalarInterval(
            math.log(self.data["lowerbound"], base),
            math.log(self.data["upperbound"], base),
        )

    def __pow__(self, exponent: Self | int | float) -> NPScalarInterval:
        """Return the interval to the power of the given exponent."""
        if isinstance(exponent, NPScalarInterval):
            pows: tuple[float, float, float, float] = (
                self.data["lowerbound"] ** exponent.data["lowerbound"],
                self.data["lowerbound"] ** exponent.data["upperbound"],
                self.data["upperbound"] ** exponent.data["lowerbound"],
                self.data["upperbound"] ** exponent.data["upperbound"],
            )
            return NPScalarInterval(min(pows), max(pows), orderguaranteed=True)
        if isinstance(exponent, int):
            return NPScalarInterval(
                self.data["lowerbound"] ** exponent,
                self.data["upperbound"] ** exponent,
            )
        return (self.log() * exponent).exp()

    def tanh(self) -> NPScalarInterval:
        """Return the hyperbolic tangens of the interval."""
        return NPScalarInterval(
            math.tanh(self.data["lowerbound"]), math.tanh(self.data["upperbound"])
        )


__all__.append("NPScalarInterval")

###############################################################################
if __name__ == "__main__":  # Small application
    if __debug__:
        basicConfig(level=INFO)
    pitest: NPScalarInterval = NPScalarInterval(3, 4, orderguaranteed=True)
    rtest: NPScalarInterval = NPScalarInterval(2.2, 2.4)
    print("========== INPUT ==========")
    print(f"pi {pitest}")
    print(f"radius {rtest}")
    print("========== OUTPUT ==========")
    print(f"diameter {rtest + rtest}")
    print("========== OUTPUT ==========")
    print(f"area {rtest * rtest * pitest}")
    print("========== OUTPUT ==========")
    print(f"volume {4 / 3 * rtest * rtest * rtest * pitest}")
