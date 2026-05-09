/* OMNI System & Interop Layer
 * C-ABI Integration Registry
 * The absolute central bridging file that standardizes cross-language FFI 
 * to adhere strictly to zero-copy memory principles as mandated by Section 17.
 */

#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * The standard Omni Tensor structure.
 * Languages like Rust, Python, Go, and Zig MUST map exactly to this layout
 * to ensure zero-copy pointer exchange.
 */
typedef struct {
    void* data;             // Pointer to raw memory (pinned)
    uint32_t dimensions[4]; // Max 4D tensors for base execution
    uint32_t ndim;          // Number of active dimensions
    uint32_t dtype;         // 0: FP32, 1: FP16, 2: INT8, 3: BF16
    uint8_t is_pinned;      // 1 if locked in RAM/VRAM
} OmniTensor;

// Global Registry State
static uint64_t active_tensor_allocations = 0;

/* Initializes the Omni C-ABI memory arena */
int32_t omni_cabi_init() {
    printf("OMNI C-ABI: Initializing Zero-Copy Native Registry.\n");
    active_tensor_allocations = 0;
    return 0; // OK
}

/* Allocates a zero-copy tensor buffer that can be shared across polyglot engines */
OmniTensor* omni_cabi_alloc_tensor(uint32_t size_in_bytes, uint32_t dtype) {
    OmniTensor* tensor = (OmniTensor*)malloc(sizeof(OmniTensor));
    if (!tensor) return NULL;

    // Use aligned_alloc or posix_memalign for AVX/SIMD compatibility
    // Using standard malloc here for generic C compliance
    tensor->data = malloc(size_in_bytes);
    if (!tensor->data) {
        free(tensor);
        return NULL;
    }

    tensor->dtype = dtype;
    tensor->is_pinned = 0;
    active_tensor_allocations++;
    
    return tensor;
}

/* Frees the cross-language tensor */
void omni_cabi_free_tensor(OmniTensor* tensor) {
    if (tensor) {
        if (tensor->data) {
            free(tensor->data);
        }
        free(tensor);
        active_tensor_allocations--;
    }
}

/* Diagnostics */
uint64_t omni_cabi_get_active_allocations() {
    return active_tensor_allocations;
}

#ifdef __cplusplus
}
#endif
