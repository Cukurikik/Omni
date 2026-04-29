#include <stdlib.h>
#include <stdio.h>

// Omni FFI return struct
typedef struct {
    double* values;
    int* row_ptrs;
    int* col_indices;
    int nnz;
    int rows;
    int cols;
    int status; // 0 = OK
} OmniSparseMatrix;

// Perform C = A * B where A is sparse CSR and B is dense
// A: (m x k), B: (k x n)
// Returns dense matrix C: (m x n)
// Caller must free returned array
__attribute__((visibility("default")))
int omni_csrmm(
    const double* val, const int* row_ptr, const int* col_ind, 
    int m, int k, 
    const double* b_dense, int n,
    double** c_dense_out
) {
    if (!val || !row_ptr || !col_ind || !b_dense || !c_dense_out) {
        return 1; // Error NULL
    }

    double* c = (double*)calloc(m * n, sizeof(double));
    if (!c) return 2; // Error OOM

    // Standard CSR * Dense mult algorithm
    for (int i = 0; i < m; ++i) {
        int row_start = row_ptr[i];
        int row_end = row_ptr[i+1];
        
        for (int p = row_start; p < row_end; ++p) {
            int j = col_ind[p];
            double v = val[p];
            
            // Multiply scalar v by row j of B, accumulate into row i of C
            for (int col = 0; col < n; ++col) {
                c[i * n + col] += v * b_dense[j * n + col];
            }
        }
    }

    *c_dense_out = c;
    return 0;
}

__attribute__((visibility("default")))
void omni_free_dense(double* ptr) {
    if (ptr) {
        free(ptr);
    }
}
