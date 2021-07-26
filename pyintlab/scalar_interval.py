"""Bastian versucht sich an Interval-Artihmetik"""
import math


class ScalarInterval:  # inheritance ob object could be suppressed
    """Klasse fuer Skalare mit Unschaerfe"""

    # __new__ is not needed as the default is sufficient

    # def __init__(self, lowerbound, upperbound):
    #     """contructor for new ScalarInterval"""
    #     self.lowerbound = lowerbound
    #     self.upperbound = upperbound
    def __init__(self, *bounds):
        """contructor for new ScalarInterval

        You can handover any count of (real) arguments, the resulting Interval
        will automatically be the convex hull (from min to max)."""
        self.lowerbound = min(bounds)
        self.upperbound = max(bounds)

    @property
    def mid(self):
        """midpoint of interval"""
        return (self.lowerbound + self.upperbound) / 2

    @property
    def rad(self):
        """radius of interval"""
        return (self.upperbound - self.lowerbound) / 2

    # <https://www.tutorialsteacher.com/python/magic-methods-in-python>
    # <https://rszalski.github.io/magicmethods/>

    def __str__(self) -> str:
        """Show a readable representation of the Interval"""
        return f"[{self.lowerbound},{self.upperbound}] <{self.mid},{self.rad}>"

    def __repr__(self) -> str:
        """Show a representation of the Interval for reconstruction"""
        return f"ScalarInterval({self.lowerbound},{self.upperbound})"

    def __ge__(self, other) -> bool:
        """dunder method for greater equals"""
        if isinstance(other, ScalarInterval):
            return self.lowerbound >= other.lowerbound
        return self.lowerbound >= other

    def __gt__(self, other) -> bool:
        """dunder method for greater than"""
        if isinstance(other, ScalarInterval):
            return self.lowerbound > other.lowerbound
        return self.lowerbound > other

    def __le__(self, other) -> bool:
        """dunder method for less equals"""
        if isinstance(other, ScalarInterval):
            return self.lowerbound <= other.lowerbound
        return self.lowerbound <= other

    def __lt__(self, other) -> bool:
        """dunder method for less than"""
        if isinstance(other, ScalarInterval):
            return self.lowerbound < other.lowerbound
        return self.lowerbound < other

    def __eq__(self, other) -> bool:
        """dunder method for equality check"""
        return (
            self.lowerbound == other.lowerbound and self.upperbound == other.upperbound
        )

    def __add__(self, other):
        """dunder method for addition"""
        if isinstance(other, ScalarInterval):
            return ScalarInterval(
                self.lowerbound + other.lowerbound, self.upperbound + other.upperbound
            )
        return ScalarInterval(self.lowerbound + other, self.upperbound + other)

    def reciproc(self):
        """build 1/x for ScalarInterval x"""
        if self:
            return ScalarInterval(1 / self.upperbound, 1 / self.lowerbound)
        raise ZeroDivisionError(
            f"Can not build the reziprocal of indefinite Interval {self}."
        )

    def __mul__(self, other):
        """dunder method for (left) multiplikation"""
        if isinstance(other, ScalarInterval):
            return ScalarInterval(
                self.lowerbound * other.lowerbound,
                self.lowerbound * other.upperbound,
                self.upperbound * other.lowerbound,
                self.upperbound * other.upperbound,
            )
        return ScalarInterval(self.lowerbound * other, self.upperbound * other)

    def __neg__(self):
        """simply switches the sign of ScalarInterval x ==> -x"""
        return ScalarInterval(-self.upperbound, -self.lowerbound)

    def __rmul__(self, other):
        """dunder method for right multiplikation"""
        if isinstance(other, ScalarInterval):
            return ScalarInterval(
                other.lowerbound * self.lowerbound,
                other.lowerbound * self.upperbound,
                other.upperbound * self.lowerbound,
                other.upperbound * self.upperbound,
            )
        return ScalarInterval(other * self.lowerbound, other * self.upperbound)

    def __bool__(self):  # python3
        """dunder method for definiteness (does not contain zero)"""
        return self.lowerbound * self.upperbound > 0

    def __sub__(self, other):
        """dunder method for subtraction"""
        if isinstance(other, ScalarInterval):
            return ScalarInterval(
                self.lowerbound - other.upperbound, self.upperbound - other.lowerbound
            )
        return ScalarInterval(self.lowerbound - other, self.upperbound - other)

    def __truediv__(self, other):
        """dunder method for true division"""
        if isinstance(other, ScalarInterval):
            return self.__mul__(other.reciproc())
        return ScalarInterval(self.lowerbound / other, self.upperbound / other)

    def __contains__(self, item) -> bool:
        """Returns boolean indicator if item is within interval."""
        if isinstance(item, ScalarInterval):
            return (
                item.lowerbound >= self.lowerbound
                and item.upperbound <= self.upperbound
            )
        return self.lowerbound <= item <= self.upperbound

    ####################################################################################
    # following are implementations of monoton increasing functions
    ####################################################################################
    def sqrt(self):
        """returns the square root of the interval"""
        return ScalarInterval(math.sqrt(self.lowerbound), math.sqrt(self.upperbound))


########################################################################################
if __name__ == "__main__":  # Test
    pitest = ScalarInterval(3, 4)
    rtest = ScalarInterval(2.2, 2.4)
    print("========== INPUT ==========")
    print(f"pi {pitest}")
    print(f"radius {rtest}")
    print("========== OUTPUT ==========")
    print(f"diameter {rtest + rtest}")
    print(f"area {rtest*rtest*pitest}")
    print(f"volume {4/3*rtest*rtest*rtest*pitest}")
