import pytest
import mpmath
from mpmath import iv
from pyintlab.scalar_interval import ScalarInterval

# Konfiguriere mpmath für Standard-Double-Präzision
mpmath.mp.dps = 15


def is_contained(si: ScalarInterval, iv_obj) -> bool:
    """
    Prüft, ob das ScalarInterval das mpmath-Intervall einschließt.
    si.lowerbound <= iv.a UND si.upperbound >= iv.b
    """
    return si.lowerbound <= float(iv_obj.a) and si.upperbound >= float(
        iv_obj.b
    )


@pytest.mark.parametrize(
    "a_range, b_range",
    [
        ((1.0, 2.0), (3.0, 4.0)),  # Positive Zahlen
        ((-2.0, -1.0), (-4.0, -3.0)),  # Negative Zahlen
        ((-1.0, 1.0), (-1.0, 1.0)),  # Null-Übergang
        ((1e-10, 2e-10), (3e-10, 4e-10)),  # Sehr kleine Zahlen
        ((1e10, 2e10), (3e10, 4e10)),  # Sehr große Zahlen
        ((0.1, 0.2), (0.1, 0.2)),  # Typische Float-ungenauigkeiten
    ],
)
def test_addition_mpmath(a_range, b_range):
    # ScalarInterval
    si_a = ScalarInterval(*a_range)
    si_b = ScalarInterval(*b_range)
    res_si = si_a + si_b

    # mpmath.iv - KORREKTUR: Grenzen als Liste übergeben
    iv_a = iv.mpf(list(a_range))
    iv_b = iv.mpf(list(b_range))
    res_iv = iv_a + iv_b

    assert is_contained(res_si, res_iv), (
        f"Addition fehlgeschlagen: {res_si} schließt {res_iv} nicht ein"
    )


@pytest.mark.parametrize(
    "a_range, b_range",
    [
        ((1.0, 2.0), (3.0, 4.0)),
        ((-2.0, -1.0), (-4.0, -3.0)),
        ((-1.0, 1.0), (-1.0, 1.0)),
        ((0.1, 0.2), (0.3, 0.4)),
    ],
)
def test_subtraction_mpmath(a_range, b_range):
    si_a = ScalarInterval(*a_range)
    si_b = ScalarInterval(*b_range)
    res_si = si_a - si_b

    iv_a = iv.mpf(list(a_range))
    iv_b = iv.mpf(list(b_range))
    res_iv = iv_a - iv_b

    assert is_contained(res_si, res_iv), (
        f"Subtraktion fehlgeschlagen: {res_si} schließt {res_iv} nicht ein"
    )


@pytest.mark.parametrize(
    "a_range, b_range",
    [
        ((1.0, 2.0), (3.0, 4.0)),
        ((-2.0, -1.0), (3.0, 4.0)),
        ((-1.0, 1.0), (-1.0, 1.0)),
        ((0.1, 0.2), (0.1, 0.2)),
    ],
)
def test_multiplication_mpmath(a_range, b_range):
    si_a = ScalarInterval(*a_range)
    si_b = ScalarInterval(*b_range)
    res_si = si_a * si_b

    iv_a = iv.mpf(list(a_range))
    iv_b = iv.mpf(list(b_range))
    res_iv = iv_a * iv_b

    assert is_contained(res_si, res_iv), (
        f"Multiplikation fehlgeschlagen: {res_si} schließt {res_iv} nicht ein"
    )


@pytest.mark.parametrize(
    "a_range, b_range",
    [
        ((1.0, 2.0), (3.0, 4.0)),
        ((1.0, 2.0), (-4.0, -3.0)),
        ((0.1, 0.2), (0.1, 0.2)),
    ],
)
def test_division_mpmath(a_range, b_range):
    si_a = ScalarInterval(*a_range)
    si_b = ScalarInterval(*b_range)
    res_si = si_a / si_b

    iv_a = iv.mpf(list(a_range))
    iv_b = iv.mpf(list(b_range))
    res_iv = iv_a / iv_b

    assert is_contained(res_si, res_iv), (
        f"Division fehlgeschlagen: {res_si} schließt {res_iv} nicht ein"
    )


def test_complex_chain_mpmath():
    a_range, b_range, c_range = (0.1, 0.2), (0.3, 0.4), (0.5, 0.6)

    si_a, si_b, si_c = (
        ScalarInterval(*a_range),
        ScalarInterval(*b_range),
        ScalarInterval(*c_range),
    )
    res_si = (si_a + si_b) * si_c / (si_a - 0.05)

    iv_a = iv.mpf(list(a_range))
    iv_b = iv.mpf(list(b_range))
    iv_c = iv.mpf(list(c_range))
    # Punktuelles Intervall für 0.05
    iv_offset = iv.mpf(0.05)
    res_iv = (iv_a + iv_b) * iv_c / (iv_a - iv_offset)

    assert is_contained(res_si, res_iv), "Kettenoperation fehlgeschlagen"
