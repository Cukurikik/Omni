/*
 * omni_ggml_tensor.c — GGML-style C Tensor Abstraction
 * Layer: System / Memory
 * Inspired by: ggerganov/ggml
 *
 * Implements a lightweight, pure C tensor struct for machine learning operations.
 * Forms the backbone of CPU-based Edge AI inference frameworks (like llama.cpp)
 * where depending on massive libraries like LibTorch is impossible. Zero mock.
 */

#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define OMNI_MAX_DIMS 4

typedef enum {
    OMNI_TYPE_F32,
    OMNI_TYPE_F16,
    OMNI_TYPE_Q4_0, // 4-bit quantized
    OMNI_TYPE_I32
} omni_type;

typedef struct {
    omni_type type;
    int n_dims;
    int64_t ne[OMNI_MAX_DIMS]; // Number of elements per dimension
    size_t nb[OMNI_MAX_DIMS];  // Stride in bytes per dimension
    
    bool is_param; // true if weight, false if activation/buffer
    void* data;
    
    char name[32]; // For debugging/graph tracing
} omni_tensor;

// Calculate element size in bytes based on type
size_t omni_type_size(omni_type type) {
    switch (type) {
        case OMNI_TYPE_F32: return 4;
        case OMNI_TYPE_F16: return 2;
        case OMNI_TYPE_I32: return 4;
        case OMNI_TYPE_Q4_0: return 0; // Handled specially in blocks
        default: return 0;
    }
}

// Allocate a new 1D Tensor
omni_tensor* omni_new_tensor_1d(omni_type type, int64_t ne0) {
    omni_tensor* t = (omni_tensor*)malloc(sizeof(omni_tensor));
    t->type = type;
    t->n_dims = 1;
    t->ne[0] = ne0;
    t->ne[1] = 1; t->ne[2] = 1; t->ne[3] = 1;
    
    size_t el_size = omni_type_size(type);
    t->nb[0] = el_size;
    t->nb[1] = t->nb[0] * t->ne[0];
    t->nb[2] = t->nb[1] * t->ne[1];
    t->nb[3] = t->nb[2] * t->ne[2];
    
    t->is_param = false;
    t->data = aligned_alloc(32, t->nb[1]); // 32-byte alignment for AVX instructions
    memset(t->name, 0, 32);
    
    return t;
}

// Allocate a new 2D Tensor
omni_tensor* omni_new_tensor_2d(omni_type type, int64_t ne0, int64_t ne1) {
    omni_tensor* t = omni_new_tensor_1d(type, ne0);
    t->n_dims = 2;
    t->ne[1] = ne1;
    
    t->nb[1] = t->nb[0] * t->ne[0];
    t->nb[2] = t->nb[1] * t->ne[1];
    
    // Reallocate data for 2D size
    free(t->data);
    t->data = aligned_alloc(32, t->nb[2]);
    
    return t;
}

void omni_free_tensor(omni_tensor* t) {
    if (t) {
        if (t->data) free(t->data);
        free(t);
    }
}
