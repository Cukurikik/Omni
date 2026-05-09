/*
 * OMNI Framework - CUDA Utility Wrappers (C)
 * Provides safe FFI boundaries for languages like Rust and Go
 * to interact with raw CUDA runtime APIs.
 */

#include <cuda_runtime.h>
#include <stdio.h>

extern "C" {

    int omni_cuda_get_device_count() {
        int count = 0;
        cudaError_t err = cudaGetDeviceCount(&count);
        if (err != cudaSuccess) {
            printf("OMNI CUDA Error: %s\n", cudaGetErrorString(err));
            return -1;
        }
        return count;
    }

    int omni_cuda_set_device(int device_id) {
        cudaError_t err = cudaSetDevice(device_id);
        if (err != cudaSuccess) {
            printf("OMNI CUDA Error: %s\n", cudaGetErrorString(err));
            return -1;
        }
        return 0;
    }

    void* omni_cuda_malloc(size_t size) {
        void* ptr = NULL;
        cudaError_t err = cudaMalloc(&ptr, size);
        if (err != cudaSuccess) {
            printf("OMNI CUDA Error: Failed to allocate %zu bytes\n", size);
            return NULL;
        }
        return ptr;
    }

    void omni_cuda_free(void* ptr) {
        if (ptr) {
            cudaFree(ptr);
        }
    }
}
