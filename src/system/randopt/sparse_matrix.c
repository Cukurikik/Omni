#include <stdbool.h>
#include <stddef.h>

typedef struct {
    void* value;
    const char* error;
    bool is_ok;
} OmniResult;

typedef struct {
    int* row_indices;
    int* col_indices;
    float* values;
    size_t nnz;
} SparseMatrix;

OmniResult multiply_sparse(SparseMatrix* A, float* vec_x, float* vec_y) {
    if (!A || !vec_x || !vec_y) {
        return (OmniResult){.value = NULL, .error = "Null pointers", .is_ok = false};
    }
    
    // C high-performance sparse matrix-vector multiplication for RandOpt
    for (size_t i = 0; i < A->nnz; ++i) {
        vec_y[A->row_indices[i]] += A->values[i] * vec_x[A->col_indices[i]];
    }
    
    return (OmniResult){.value = vec_y, .error = NULL, .is_ok = true};
}
