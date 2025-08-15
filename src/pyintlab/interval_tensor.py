"""class for Order >= 1 Tensors of Intervals"""

from numpy import ndarray
from scalar_interval import ScalarInterval


class IntervallTensor(ndarray):
    def __new__(cls, input_array) -> "IntervallTensor":
        return array.__new__(cls, input_array, dtype=ScalarInterval)


#    def __init__(self, input_array) -> None:
#        super().__init__()
#        self.input_array = input_array

# def __array_finalize__(self, obj):
#
#
