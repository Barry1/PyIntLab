"""Bastian versucht sich an Interval-Arithmetik."""
import math

import pytest

from .scalar_interval import ScalarInterval  # pylint: disable=E0402


def test_scalar_contains() -> None:
    """Function for PyTest check keyword IN and thus __contains__ for scalar."""
    assert math.pi in ScalarInterval(3, math.sqrt(10))


def test_repr() -> None:
    """Function for rebuilding Interval by __repr__."""
    testinterval = ScalarInterval(8, 11)
    assert testinterval == eval(repr(testinterval))  # pylint: disable=W0123


def test_arith() -> None:
    """First arithmetic test."""
    aint = ScalarInterval(3, 4)
    bint = ScalarInterval(-2, 0.1)
    assert (
        ScalarInterval(
            *[
                a - b / a
                for a in [aint.lowerbound, aint.upperbound]
                for b in [bint.lowerbound, bint.upperbound]
            ]
        )
        in aint - bint / aint
    )


def test_div_zero() -> None:
    """Assert that Division by zero raises Exception."""
    with pytest.raises(
        ZeroDivisionError
    ) as e_info:  # noqa: W0612 # pylint: disable=unused-variable
        _ = ScalarInterval(-0.42, 0.3) / 0


def test_div_zero2() -> None:
    """Assert that Division by zero raises Exception."""
    with pytest.raises(
        ZeroDivisionError
    ) as e_info:  # noqa: W0612 # pylint: disable=unused-variable
        _ = 42 / ScalarInterval(-0.42, 0.3)


def test_div_zero3() -> None:
    """Assert that Division by zero raises Exception."""
    with pytest.raises(
        ZeroDivisionError
    ) as e_info:  # noqa: W0612 # pylint: disable=unused-variable
        _ = ScalarInterval(2.7, 3.1415) / ScalarInterval(-0.42, 0.3)
