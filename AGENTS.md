# AGENTS.md - Learnings für AI-Assistenten bei der Optimierung von PyIntLab

## 🚨 Critical Workflow Rules

1. **Single Source of Truth:** Always use the current `main` branch of the online repository `https://github.com/Barry1/PyIntLab` as the basis for all code generation and modifications.
1. **No Local Files:** Do NOT use local files unless explicitly instructed by the user. The online repository is the authoritative source.
1. **Commit Reference:** When possible, reference the specific commit hash (e.g., `6716995`) to ensure reproducibility.
1. **Code Validation:** NEVER send code that has not been logically validated. Specifically:

- Verify that all method calls exist on the target objects (e.g., `list` has no `.reshape()`).
- Verify that array shapes and dtypes are compatible before sending.
- If in doubt, simulate the code execution mentally or via tool before presenting it.

5. **Graphical output** via kroki (for example plantuml or mermaid) if not possible with python script to generate.

## API Conventions

- **ScalarInterval Attributes:** Use `lowerbound` and `upperbound` (NOT `lower` and `upper`).
- **ArrayInterval Constructor:** Accepts a single argument (list of tuples or structured array), NOT two separate arrays.
- **RoundingContext:** Use `RoundingMode.DOWNWARD` and `RoundingMode.UPWARD` constants.
- **Structured Dtype:** `[("lowerbound", "<f8"), ("upperbound", "<f8")]`

## Architecture Decisions

### Interval Representation

- **ScalarInterval:** The core reference implementation. Handles rigorous outward rounding for single intervals using `math.nextafter`. This class is the "ground truth" for correctness.
- **ArrayInterval:** Implemented using a NumPy structured dtype. This approach was chosen for memory efficiency and the potential for vectorized operations.

### Rigorous Outward Rounding

- **Strategy:** To guarantee rigorous results in NumPy operations, the C-level floating-point rounding mode is manipulated using `ctypes`.
- **Implementation:** A `RoundingContext` manager is used to temporarily switch the rounding mode:
  - **Downward (`-inf`):** Used when computing lower bounds.
  - **Upward (`+inf`):** Used when computing upper bounds.
- **Platform Specifics:**
  - **Unix-like:** Uses `fesetround` from the standard C library (`libc`).
  - **Windows:** Uses `_control87` from `msvcrt` with mask `0x0300` and value `mode << 10`.
- **Thread Safety:** Rounding modes are typically thread-local. However, NumPy's internal multi-threaded BLAS libraries may interfere with rigorous computations. It is recommended to perform rigorous computations in single-threaded contexts or with controlled parallelization.

### Performance Optimization

- **Matrix Multiplication (`__matmul__`):**
  - Implemented using vectorized NumPy operations with broadcasting.
  - To maintain rigor, the lower bound is computed by summing the minimum products (with downward rounding), and the upper bound is computed by summing the maximum products (with upward rounding).
  - This avoids Python loops and leverages NumPy's optimized C-backend while ensuring outward rounding.

## Testing Strategy

- **ScalarInterval Validation:** Tested against `mpmath.iv` to ensure that `ScalarInterval` results rigorously contain the `mpmath.iv` results.
- **ArrayInterval Validation:** Tested against element-wise `ScalarInterval` operations to verify that the `RoundingContext` logic produces identical rigorous results.
- **Test Files:**
  - `test_scalar_interval.py`: Contains tests against `mpmath.iv`.
  - `test_array_interval_vs_scalar.py`: Contains tests comparing `ArrayInterval` to `ScalarInterval`.

## Future Considerations

- **Tensor Support:** The current `ArrayInterval` implementation is designed for 2D matrices. Extending to N-dimensional tensors may require further optimization of the broadcasting logic.
- **Additional Operations:** Implementing more advanced interval operations (e.g., division, square root, exponential) will require careful handling of the `RoundingContext` to maintain rigor.
