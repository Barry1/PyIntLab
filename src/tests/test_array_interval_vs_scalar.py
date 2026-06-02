"""
Tests to validate ArrayInterval against ScalarInterval.

These tests ensure that the ArrayInterval implementation produces results
identical to the element-wise application of ScalarInterval operations.
"""

import numpy as np
import pytest

from pyintlab.array_interval import ArrayInterval
from pyintlab.scalar_interval import ScalarInterval


class TestArrayIntervalVsScalar:
    """Compare ArrayInterval operations with element-wise ScalarInterval operations."""

    def test_addition_consistency(self):
        """Verify that ArrayInterval addition matches ScalarInterval addition."""
        l1, u1 = np.array([1.0, 2.0, 3.0]), np.array([1.1, 2.2, 3.3])
        l2, u2 = np.array([0.5, 1.5, 2.5]), np.array([0.6, 1.6, 2.6])

        ai1 = ArrayInterval(list(zip(l1, u1)))
        ai2 = ArrayInterval(list(zip(l2, u2)))

        result_ai = ai1 + ai2

        # Compute reference using ScalarInterval
        ref_lower = []
        ref_upper = []
        for i in range(len(l1)):
            si1 = ScalarInterval(l1[i], u1[i])
            si2 = ScalarInterval(l2[i], u2[i])
            res_si = si1 + si2
            ref_lower.append(res_si.lowerbound)
            ref_upper.append(res_si.upperbound)

        assert np.allclose(result_ai.lowerbound, ref_lower)
        assert np.allclose(result_ai.upperbound, ref_upper)

    def test_subtraction_consistency(self):
        """Verify that ArrayInterval subtraction matches ScalarInterval subtraction."""
        l1, u1 = np.array([5.0, 10.0]), np.array([5.5, 10.5])
        l2, u2 = np.array([1.0, 2.0]), np.array([1.2, 2.2])

        ai1 = ArrayInterval(list(zip(l1, u1)))
        ai2 = ArrayInterval(list(zip(l2, u2)))

        result_ai = ai1 - ai2

        ref_lower = []
        ref_upper = []
        for i in range(len(l1)):
            si1 = ScalarInterval(l1[i], u1[i])
            si2 = ScalarInterval(l2[i], u2[i])
            res_si = si1 - si2
            ref_lower.append(res_si.lowerbound)
            ref_upper.append(res_si.upperbound)

        assert np.allclose(result_ai.lowerbound, ref_lower)
        assert np.allclose(result_ai.upperbound, ref_upper)

    def test_multiplication_consistency(self):
        """Verify that ArrayInterval multiplication matches ScalarInterval multiplication."""
        l1, u1 = np.array([-2.0, 3.0]), np.array([-1.0, 4.0])
        l2, u2 = np.array([1.0, -5.0]), np.array([2.0, -4.0])

        ai1 = ArrayInterval(list(zip(l1, u1)))
        ai2 = ArrayInterval(list(zip(l2, u2)))

        result_ai = ai1 * ai2

        ref_lower = []
        ref_upper = []
        for i in range(len(l1)):
            si1 = ScalarInterval(l1[i], u1[i])
            si2 = ScalarInterval(l2[i], u2[i])
            res_si = si1 * si2
            ref_lower.append(res_si.lowerbound)
            ref_upper.append(res_si.upperbound)

        assert np.allclose(result_ai.lowerbound, ref_lower)
        assert np.allclose(result_ai.upperbound, ref_upper)

    def test_matmul_consistency(self):
        """Verify that ArrayInterval matrix multiplication matches ScalarInterval matrix multiplication."""
        # Create 2x2 interval matrices
        l1 = np.array([[1.0, 2.0], [3.0, 4.0]])
        u1 = np.array([[1.1, 2.1], [3.1, 4.1]])
        l2 = np.array([[0.5, 0.5], [0.5, 0.5]])
        u2 = np.array([[0.6, 0.6], [0.6, 0.6]])

        # Correct construction: create structured array directly
        ai1 = ArrayInterval(
            np.array(
                [
                    [(l1[0, 0], u1[0, 0]), (l1[0, 1], u1[0, 1])],
                    [(l1[1, 0], u1[1, 0]), (l1[1, 1], u1[1, 1])],
                ],
                dtype=[("lowerbound", "<f8"), ("upperbound", "<f8")],
            )
        )

        ai2 = ArrayInterval(
            np.array(
                [
                    [(l2[0, 0], u2[0, 0]), (l2[0, 1], u2[0, 1])],
                    [(l2[1, 0], u2[1, 0]), (l2[1, 1], u2[1, 1])],
                ],
                dtype=[("lowerbound", "<f8"), ("upperbound", "<f8")],
            )
        )

        result_ai = ai1 @ ai2

        # Reference computation using ScalarInterval
        ref_lower = np.zeros((2, 2))
        ref_upper = np.zeros((2, 2))

        for i in range(2):
            for j in range(2):
                sum_lower = 0.0
                sum_upper = 0.0
                for k in range(2):
                    si_a = ScalarInterval(l1[i, k], u1[i, k])
                    si_b = ScalarInterval(l2[k, j], u2[k, j])
                    prod = si_a * si_b
                    sum_lower += prod.lowerbound
                    sum_upper += prod.upperbound
                ref_lower[i, j] = sum_lower
                ref_upper[i, j] = sum_upper

        assert np.allclose(result_ai.lowerbound, ref_lower)
        assert np.allclose(result_ai.upperbound, ref_upper)
