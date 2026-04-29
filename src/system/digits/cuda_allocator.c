#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <cuda_runtime.h>

// OMNI DIGITS: Bare-metal CUDA memory allocator
// Bypasses high-level overhead for direct GPU memory pool management
// Source: NVIDIA/DIGITS

typedef enum {
    ALLOC_SUCCESS = 0,
    ALLOC_ERR_OOM = 1,
    ALLOC_ERR_INVALID = 2
} AllocError;

typedef struct {
    void* d_ptr;
    size_t size;
    int device_id;
} CudaMemBlock;

// Monadic-style error returning via struct
typedef struct {
    CudaMemBlock block;
    AllocError error;
} AllocResult;

AllocResult omni_cuda_malloc(size_t size, int device_id) {
    AllocResult res;
    res.error = ALLOC_SUCCESS;
    res.block.size = size;
    res.block.device_id = device_id;
    res.block.d_ptr = NULL;

    cudaError_t set_err = cudaSetDevice(device_id);
    if (set_err != cudaSuccess) {
        res.error = ALLOC_ERR_INVALID;
        return res;
    }

    cudaError_t err = cudaMalloc(&res.block.d_ptr, size);
    if (err != cudaSuccess) {
        res.error = ALLOC_ERR_OOM;
    }

    return res;
}

AllocError omni_cuda_free(CudaMemBlock* block) {
    if (!block || !block->d_ptr) {
        return ALLOC_ERR_INVALID;
    }
    
    cudaSetDevice(block->device_id);
    cudaError_t err = cudaFree(block->d_ptr);
    
    if (err != cudaSuccess) {
        return ALLOC_ERR_INVALID;
    }
    
    block->d_ptr = NULL;
    block->size = 0;
    return ALLOC_SUCCESS;
}

// Zero-copy host-to-device pinned memory allocation
AllocResult omni_cuda_malloc_host(size_t size) {
    AllocResult res;
    res.error = ALLOC_SUCCESS;
    res.block.size = size;
    res.block.device_id = -1; // Host memory

    cudaError_t err = cudaMallocHost(&res.block.d_ptr, size);
    if (err != cudaSuccess) {
        res.error = ALLOC_ERR_OOM;
    }
    return res;
}
