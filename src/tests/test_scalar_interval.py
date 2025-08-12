"""Bastian versucht sich an Interval-Arithmetik."""

import math

from pytest import raises

from pyintlab import ScalarInterval  # pylint: disable=E0402


def test_abs() -> None:
    assert abs(ScalarInterval(1, 2)) == ScalarInterval(1, 2)  # nosec B101
    assert abs(ScalarInterval(-4, 3)) == ScalarInterval(0, 4)  # nosec B101
    assert abs(ScalarInterval(-5, -6)) == ScalarInterval(5, 6)  # nosec B101


def test_explog_in() -> None:
    """Test if x in e^log(x)."""
    for myx in [
        ScalarInterval(math.pi),
        ScalarInterval(math.pi, math.sqrt(10)),
    ]:
        assert myx in myx.log().exp()  # nosec B101


def test_logexp_in() -> None:
    """Test if x in log(e^x)."""
    for myx in [
        ScalarInterval(math.pi),
        ScalarInterval(math.pi, math.sqrt(10)),
    ]:
        assert myx in myx.exp().log()  # nosec B101


def test_scalar_contains() -> None:
    """Function for PyTest check keyword IN (__contains__) for scalar."""
    assert math.pi in ScalarInterval(3, math.sqrt(10))  # nosec B101


def test_repr() -> None:
    """Function for rebuilding Interval by __repr__."""
    testinterval = ScalarInterval(8, 11)
    assert testinterval == eval(  # nosec B101 B307
        repr(testinterval)
    )  # pylint: disable=W0123 nosec B101


def test_arith() -> None:
    """First arithmetic test."""
    aint = ScalarInterval(3, 4)
    bint = ScalarInterval(-2, 0.1)
    assert (  # nosec B101
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
    with raises(ZeroDivisionError) as _:
        _ = ScalarInterval(-0.42, 0.3) / 0


def test_div_zero2() -> None:
    """Assert that Division by zero raises Exception."""
    with raises(ZeroDivisionError) as _:
        _ = 42 / ScalarInterval(-0.42, 0.3)


def test_div_zero3() -> None:
    """Assert that Division by zero raises Exception."""
    with raises(ZeroDivisionError) as _:
        _ = ScalarInterval(2.7, 3.1415) / ScalarInterval(-0.42, 0.3)
