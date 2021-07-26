"""Bastian versucht sich an Interval-Artihmetik"""
import math

from .scalar_interval import ScalarInterval


def test_scalar_contains() -> None:
    """Function for PyTest check keyword IN and thus __contains__ for scalar."""
    assert math.pi in ScalarInterval(3, math.sqrt(10))


def test_repr() -> None:
    """Function for rebuilding Interval by __repr__"""
    testinterval = ScalarInterval(8, 11)
    assert testinterval == eval(repr(testinterval))  # noqa: W0123
