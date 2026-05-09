// OMNI System Layer: CUDA GPU Bridge
#include <cuda_runtime.h>

extern "C" {
    void omni_cuda_malloc(void** ptr, size_t size) {
        cudaMalloc(ptr, size);
    }
    
    void omni_cuda_free(void* ptr) {
        cudaFree(ptr);
    }

    void omni_cuda_memcpy_host_to_device(void* dst, void* src, size_t size) {
        cudaMemcpy(dst, src, size, cudaMemcpyHostToDevice);
    }
}
