#include <cstdint>
#include <cmath>

extern "C" {

// FFI export for deterministic high-speed Cholesky decomposition of Positive Definite Matrices
// Solves A = L * L^T. Input is NxN matrix stored in row-major order.
void omni_gpflow_cholesky(
    const double* A, 
    int32_t n, 
    double* L, 
    int32_t* err_code
) {
    if (!err_code) return;

    if (!A || !L || n <= 0) {
        *err_code = -1;
        return;
    }

    // Initialize L with zeros
    for (int32_t i = 0; i < n * n; ++i) {
        L[i] = 0.0;
    }

    // Deterministic Cholesky-Banachiewicz algorithm
    for (int32_t i = 0; i < n; i++) {
        for (int32_t j = 0; j <= i; j++) {
            double sum = 0.0;

            if (j == i) { // Diagonal element
                for (int32_t k = 0; k < j; k++) {
                    sum += std::pow(L[j * n + k], 2);
                }
                
                double diag_val = A[j * n + j] - sum;
                
                // Must be positive definite
                if (diag_val <= 1e-12) {
                    *err_code = -2; // Matrix is not positive definite mathematically
                    return;
                }
                
                L[j * n + j] = std::sqrt(diag_val);
            } else { // Lower triangular elements
                for (int32_t k = 0; k < j; k++) {
                    sum += (L[i * n + k] * L[j * n + k]);
                }
                
                L[i * n + j] = (A[i * n + j] - sum) / L[j * n + j];
            }
        }
    }

    *err_code = 0;
}

}
