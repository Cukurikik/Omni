// omni_cuda_utils.cu — CUDA Memory & Device Utilities
// Layer: System / CUDA
//
// Safe wrapper functions around the CUDA Runtime API for device queries
// and streamlined, error-checked memory allocations.

#include <cuda_runtime.h>
#include <stdio.h>
#include <stdlib.h>

#define CHECK_CUDA(call) \
do { \
    cudaError_t err = call; \
    if (err != cudaSuccess) { \
        fprintf(stderr, "CUDA Error at %s:%d - %s\n", __FILE__, __LINE__, cudaGetErrorString(err)); \
        exit(EXIT_FAILURE); \
    } \
} while (0)

extern "C" {

/**
 * Returns the amount of free and total VRAM on the specified GPU.
 */
void omni_cuda_get_mem_info(int device_id, size_t* free_mem, size_t* total_mem) {
    CHECK_CUDA(cudaSetDevice(device_id));
    CHECK_CUDA(cudaMemGetInfo(free_mem, total_mem));
}

/**
 * Allocates VRAM on the GPU securely.
 */
void* omni_cuda_malloc(size_t size) {
    void* d_ptr = NULL;
    CHECK_CUDA(cudaMalloc(&d_ptr, size));
    return d_ptr;
}

/**
 * Frees VRAM on the GPU.
 */
void omni_cuda_free(void* d_ptr) {
    if (d_ptr) {
        CHECK_CUDA(cudaFree(d_ptr));
    }
}

/**
 * Synchronizes the entire device (blocks CPU until GPU is idle).
 */
void omni_cuda_sync(int device_id) {
    CHECK_CUDA(cudaSetDevice(device_id));
    CHECK_CUDA(cudaDeviceSynchronize());
}

} // extern "C"
