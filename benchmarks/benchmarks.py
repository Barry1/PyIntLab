"""ASV Benchmarks für PyIntLab – ScalarInterval und zukünftige NumPy-Varianten."""

import numpy

from pyintlab.scalar_interval import ScalarInterval


class TimeScalarInterval:
    """Benchmark verschiedener Operationen auf ScalarInterval."""

    # Setup wird einmal pro Benchmark-Gruppe ausgeführt
    def setup(self):
        self.small_pos = [
            ScalarInterval(i, i + 2) for i in 100 * numpy.random.random(100)
        ]
        self.small_neg = [
            ScalarInterval(-i - 3, -i - 1)
            for i in 100 * numpy.random.random(100)
        ]
        self.mixed = [
            ScalarInterval(-i, i + 1) for i in 100 * numpy.random.random(100)
        ]

        self.a = ScalarInterval(1, 3)
        self.b = ScalarInterval(2, 5)
        self.c = ScalarInterval(-4, -1)

    # ---------- Arithmetik ----------
    def time_add(self):
        for x in self.small_pos:
            _ = x + self.a

    def time_sub(self):
        for x in self.small_pos:
            _ = x - self.a

    def time_mul_positive(self):
        for x in self.small_pos:
            _ = x * self.a

    def time_mul_negative(self):
        for x in self.small_neg:
            _ = x * self.c

    def time_mul_mixed(self):
        for x in self.mixed:
            _ = x * self.a

    def time_truediv(self):
        for x in self.small_pos:
            _ = x / self.b

    def time_inplace_add(self):
        x = ScalarInterval(10, 20)
        for _ in range(100):
            x += self.a

    def time_inplace_mul(self):
        x = ScalarInterval(10, 20)
        for _ in range(100):
            x *= self.a

    # ---------- Sonstiges ----------
    def time_abs(self):
        for x in self.mixed:
            _ = abs(x)

    def time_neg(self):
        for x in self.mixed:
            _ = -x

    def time_mid_rad(self):
        for x in self.small_pos:
            _ = x.mid
            _ = x.rad

    def time_bool(self):
        for x in self.mixed:
            _ = bool(x)


class TimeScalarIntervalLarge:
    """Benchmarks mit größeren Listen (Skalierungsverhalten)."""

    params = [1_000, 10_000, 100_000]
    param_names = ["size"]

    def setup(self, size):
        self.intervals = [
            ScalarInterval(i % 10, i % 10 + 2)
            for i in size * numpy.random.random(size)
        ]
        self.a = ScalarInterval(3, 7)

    def time_add_large(self, size):
        for x in self.intervals:
            _ = x + self.a

    def time_mul_large(self, size):
        for x in self.intervals:
            _ = x * self.a


class TimeCreation:
    """Benchmark für die Erzeugung von Intervallen."""

    def setup(self):
        self.values = list(1000 * numpy.random.random(1000))

    def time_create_single(self):
        for v in self.values:
            _ = ScalarInterval(v, v + 1)

    def time_create_from_tuple(self):
        for v in self.values:
            _ = ScalarInterval(v, v + 2, _orderguaranteed=True)
