"""Bastian versucht sich an Interval-Arithmetik."""
import numpy

from .scalar_interval import ScalarInterval  # pylint: disable=E0402


# https://numpy.org/doc/stable/user/basics.dispatch.html
# https://numpy.org/doc/stable/user/basics.subclassing.html
# https://numpy.org/doc/stable/user/basics.subclassing.html#a-brief-python-primer-on-new-and-init
# https://numpy.org/doc/stable/reference/arrays.scalars.html#numpy.inexact
###########################################
# https://pypi.org/project/uncertainties/ #
###########################################
def test_matrix_product() -> None:
    """Two simple matrices of ScalarIntervals in dot product."""
    left_matrix: numpy.ndarray = numpy.array(
        [
            [ScalarInterval(1), ScalarInterval(3)],
            [ScalarInterval(2), ScalarInterval(4)],
        ],
        dtype=ScalarInterval,
    )
    right_matrix: numpy.ndarray = numpy.array(
        [
            [ScalarInterval(5), ScalarInterval(7)],
            [ScalarInterval(6), ScalarInterval(8)],
        ],
        dtype=ScalarInterval,
    )
    result_matrix = left_matrix.dot(right_matrix)
    assert numpy.array_equal(
        result_matrix,
        numpy.array(
            [
                [ScalarInterval(23), ScalarInterval(31)],
                [ScalarInterval(34), ScalarInterval(46)],
            ],
            dtype=ScalarInterval,
        ),
    )
