"""class for Order >= 1 Tensors of Intervals."""

from typing import Self

from numpy import array, ndarray, unravel_index

# from .scalar_interval import ScalarInterval
from pyintlab.numpydt_scalar_interval import NPScalarInterval as ScalarInterval

# https://numpy.org/doc/stable/user/basics.subclassing.html


class IntervallTensor(ndarray):
    """Class for Order >= 1 Tensors of Intervals."""

    def __new__(cls, input_array) -> Self:
        return array(object=input_array, dtype=ScalarInterval).view(cls)


def solve(A, b):
    """Solve the linear equation Ax = b."""
    [rows, cols] = A.shape
    # Erster Schritt
    pivpos = abs(A).argmax()
    therow, thecol = unravel_index(pivpos, A.shape)
    b[therow, 0] /= b[therow, 0]
    A[therow, :] /= A[therow, thecol]
    A[therow, thecol] = 1
    for runrow in range(rows):
        if runrow != therow:
            b[runrow, 0] -= A[runrow, thecol] * b[therow, 0]
            A[runrow, :] -= A[therow, :] * A[runrow, thecol]
            A[runrow, thecol] = 0
    print(A, "\n", b)
    # Zweiter Schritt
    pivpos = abs(A).argmax()
    [therow, thecol] = unravel_index(pivpos, A.shape)
    b[therow, 0] /= b[therow, 0]
    A[therow, :] /= A[therow, thecol]
    A[therow, thecol] = 1
    print(A, "\n", b)


if __name__ == "__main__":
    A = IntervallTensor(
        [
            [ScalarInterval(1, 2), ScalarInterval(3, 4)],
            [ScalarInterval(5, 6), ScalarInterval(7, 8)],
        ]
    )
    b = A @ [[1], [1]]
    solve(A, b)
