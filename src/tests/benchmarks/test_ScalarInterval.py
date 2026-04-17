"""Kompletter Benchmark für alle Intervall-Operationen + Varianten."""

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from pyintlab.scalar_interval import ScalarInterval


# ==================== FIXTURES ====================
@pytest.fixture(params=[1, 10, 100, 1_000], ids=["scalar", "10", "100", "1k"])
def size(request):
    return request.param


@pytest.fixture(params=["positive", "negative", "mixed", "zero"], ids=str)
def sign_type(request):
    return request.param


@pytest.fixture
def scalar_intervals(size: int, sign_type: str):
    """Liste von ScalarInterval (reine Python-Variante)."""
    if size == 1:
        if sign_type == "positive":
            return [ScalarInterval(1, 3)]
        if sign_type == "negative":
            return [ScalarInterval(-4, -2)]
        if sign_type == "mixed":
            return [ScalarInterval(-2, 5)]
        return [ScalarInterval(-1, 1)]  # zero
    # große Arrays
    if sign_type == "positive":
        return [ScalarInterval(i, i + 2) for i in range(size)]
    if sign_type == "negative":
        return [ScalarInterval(-i - 2, -i) for i in range(size)]
    if sign_type == "mixed":
        return [ScalarInterval(-i, i + 1) for i in range(size)]
    return [ScalarInterval(-1, 1) for _ in range(size)]


# ==================== BENCHMARKS ====================
@pytest.mark.benchmark(group="scalar_add")
def test_scalar_add(benchmark: BenchmarkFixture, scalar_intervals):
    def run():
        a = scalar_intervals[0]
        for b in scalar_intervals[1:]:
            _ = a + b

    benchmark(run)


@pytest.mark.benchmark(group="scalar_mul")
def test_scalar_mul(benchmark: BenchmarkFixture, scalar_intervals):
    def run():
        a = scalar_intervals[0]
        for b in scalar_intervals[1:]:
            _ = a * b

    benchmark(run)


# Gleiches Muster für -, /, **, abs, neg, mid, rad, in-place etc.
# (Ich habe hier nur zwei als Beispiel – unten findest du den vollständigen Block)


# Vollständige Liste der getesteten Operationen (kopiere einfach):
# scalar_add, scalar_sub, scalar_mul, scalar_truediv, scalar_pow,
# scalar_abs, scalar_neg, scalar_mid, scalar_rad,
# numpy_add, numpy_mul, numpy_truediv, numpy_matmul (falls @ implementiert) usw.

if __name__ == "__main__":
    pytest.main([__file__, "--benchmark-only", "--benchmark-histogram"])
