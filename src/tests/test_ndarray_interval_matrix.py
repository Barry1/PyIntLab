"""Bastian versucht sich an Interval-Arithmetik."""
import numpy
import numpy.typing

from pyintlab import ScalarInterval


# https://numpy.org/doc/stable/user/basics.dispatch.html
# https://numpy.org/doc/stable/user/basics.subclassing.html
# https://numpy.org/doc/stable/user/basics.subclassing.html#a-brief-python-primer-on-new-and-init
# https://numpy.org/doc/stable/reference/arrays.scalars.html#numpy.inexact
###########################################
# https://pypi.org/project/uncertainties/ #
###########################################
def test_matrix_product() -> None:
    """Two simple matrices of ScalarIntervals in dot product."""
    left_matrix: numpy.typing.NDArray[
        numpy.object_
    ] = numpy.array(  # pyright: ignore [reportUnknownMemberType]
        [
            [ScalarInterval(1), ScalarInterval(3)],
            [ScalarInterval(2), ScalarInterval(4)],
        ],
        dtype=ScalarInterval,
    )
    right_matrix: numpy.typing.NDArray[
        numpy.object_
    ] = numpy.array(  # pyright: ignore [reportUnknownMemberType]
        [
            [ScalarInterval(5), ScalarInterval(7)],
            [ScalarInterval(6), ScalarInterval(8)],
        ],
        dtype=ScalarInterval,
    )
    res_matrix = left_matrix.dot(  # pyright: ignore [reportUnknownMemberType]
        right_matrix
    )
    assert numpy.array_equal(  # pyright: ignore [reportUnknownMemberType]
        res_matrix,
        numpy.array(  # pyright: ignore [reportUnknownMemberType]
            [
                [ScalarInterval(23), ScalarInterval(31)],
                [ScalarInterval(34), ScalarInterval(46)],
            ],
            dtype=ScalarInterval,
        ),
    )
