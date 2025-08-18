"""Bastian is working on interval arithmetics."""

from logging import Logger, getLogger
from typing import TYPE_CHECKING

import numpy

if not TYPE_CHECKING:
    try:
        # pylint: disable=redefined-builtin
        from Cython import float
    except ImportError:
        thelogger.info("No cython here. Using python float instead.")
scalar_interval_dtype: numpy.dtype[numpy.void] = numpy.dtype(
    [("lowerbound", numpy.float64), ("upperbound", numpy.float64)]
)
thelogger: Logger = getLogger(__name__)
__all__: list[str] = []


class NPScalarInterval:  # inheritance from object could be suppressed
    """Class for scalars with uncertainty."""

    __slots__: tuple[str] = ("data",)
    # measured with from pympler import asizeof by using __slots__ memory
    # usage of one ScalerInterval has been reduced from 504 to 96 bytes.
    # That is less than 20% of the original size.
    data: numpy.ndarray
    # __new__ is not needed as the default is sufficient

    def __init__(self, *bounds: float, orderguaranteed: bool = False) -> None:
        """Construct for new ScalarInterval.

        You can handover any number of (real) arguments, the resulting Interval
        will automatically be the convex hull (from min to max).
        """
        if not bounds:
            raise ValueError("At least one bound must be provided.")
        if orderguaranteed:
            self.data = numpy.array(
                [(bounds[0], bounds[-1])], dtype=scalar_interval_dtype
            )
        else:
            self.data = numpy.array(
                [min(bounds), max(bounds)], dtype=scalar_interval_dtype
            )


if __name__ == "__main__":
