import pytest
import numpy as np
from pyintlab.scalar_interval import ScalarInterval
from pyintlab.array_interval import ArrayInterval

def test_array_creation():
    data = [(1.0, 2.0), (3.0, 4.0)]
    arr = ArrayInterval(data)
    assert arr.shape == (2,)
    assert arr.lowerbound[0] == 1.0
    assert arr.upperbound[1] == 4.0

def test_addition_vs_scalar():
    # Create array of ScalarIntervals
    si1 = ScalarInterval(1.0, 2.0)
    si2 = ScalarInterval(3.0, 4.0)
    
    # Create ArrayInterval
    arr = ArrayInterval([(si1.lowerbound, si1.upperbound), 
                         (si2.lowerbound, si2.upperbound)])
    
    # Perform addition
    res = arr + 1.0
    
    # Verify against ScalarInterval
    assert res.lowerbound[0] == (si1 + 1.0).lowerbound
    assert res.upperbound[1] == (si2 + 1.0).upperbound

def test_multiplication_rigorous():
    # Case: [-1, 1] * [-1, 1] = [-1, 1]
    arr = ArrayInterval([(-1.0, 1.0)])
    res = arr * arr
    
    assert res.lowerbound[0] == -1.0
    assert res.upperbound[0] == 1.0

def test_matmul():
    # 2x2 Matrix * 2x1 Vector
    A = ArrayInterval([
        [(1.0, 1.1), (2.0, 2.1)],
        [(3.0, 3.1), (4.0, 4.1)]
    ])
    B = ArrayInterval([
        [(1.0, 1.1)],
        [(1.0, 1.1)]
    ])
    
    res = A @ B
    
    # Manual check for first element: [1, 1.1]*[1, 1.1] + [2, 2.1]*[1, 1.1]
    # = [1, 1.21] + [2, 2.31] = [3, 3.52]
    assert res.lowerbound[0, 0] >= 3.0
    assert res.upperbound[0, 0] >= 3.52