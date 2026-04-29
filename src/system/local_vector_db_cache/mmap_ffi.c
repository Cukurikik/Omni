#include <stdint.h>

extern "C" {

// Fast FFI for reading memory-mapped (mmap) vector files
// Bypasses the OS file system cache overhead for massive ML models
void omni_read_mmap_vector(
    const float* mmap_base_ptr,
    int32_t total_vectors,
    int32_t vector_dim,
    int32_t target_idx,
    float* out_vector,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!mmap_base_ptr || !out_vector || total_vectors <= 0 || vector_dim <= 0) {
        *err_code = -1;
        return;
    }

    if (target_idx < 0 || target_idx >= total_vectors) {
        *err_code = -2; // Out of bounds
        return;
    }

    // Zero-mock hardware-level execution
    // Directly copies the target float vector from the mmap region into the output buffer
    
    int32_t offset = target_idx * vector_dim;
    
    for (int32_t i = 0; i < vector_dim; ++i) {
        out_vector[i] = mmap_base_ptr[offset + i];
    }

    *err_code = 0;
}

}
