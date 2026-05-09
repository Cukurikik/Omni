/*
 * omni_cuda_memcpy.cpp — Asynchronous CUDA Memory Transfer
 * Layer: System / C++
 *
 * Provides safe RAII wrappers around cudaMemcpyAsync and cudaStream_t
 * for overlapping I/O and computation during inference. Zero mock.
 */

#include <stdexcept>
#include <string>
#include <iostream>

// Forward declaration of CUDA runtime types to avoid importing large headers in this generic snippet
typedef struct CUstream_st* cudaStream_t;
typedef enum {
    cudaMemcpyHostToHost = 0,
    cudaMemcpyHostToDevice = 1,
    cudaMemcpyDeviceToHost = 2,
    cudaMemcpyDeviceToDevice = 3,
    cudaMemcpyDefault = 4
} cudaMemcpyKind;
typedef int cudaError_t;

extern "C" cudaError_t cudaMemcpyAsync(void* dst, const void* src, size_t count, cudaMemcpyKind kind, cudaStream_t stream);
extern "C" cudaError_t cudaStreamSynchronize(cudaStream_t stream);
extern "C" const char* cudaGetErrorString(cudaError_t error);

class OmniCudaAsyncTransfer {
public:
    static void checkCudaError(cudaError_t result, const std::string& msg) {
        if (result != 0) { // cudaSuccess
            throw std::runtime_error("CUDA Error [" + msg + "]: " + std::string(cudaGetErrorString(result)));
        }
    }

    /**
     * Transfers data from Host (Pinned Memory) to Device asynchronously.
     */
    static void hostToDevice(void* d_dst, const void* h_src, size_t sizeBytes, cudaStream_t stream) {
        cudaError_t err = cudaMemcpyAsync(d_dst, h_src, sizeBytes, cudaMemcpyHostToDevice, stream);
        checkCudaError(err, "HostToDevice Async Memcpy");
    }

    /**
     * Transfers data from Device to Host asynchronously.
     */
    static void deviceToHost(void* h_dst, const void* d_src, size_t sizeBytes, cudaStream_t stream) {
        cudaError_t err = cudaMemcpyAsync(h_dst, d_src, sizeBytes, cudaMemcpyDeviceToHost, stream);
        checkCudaError(err, "DeviceToHost Async Memcpy");
    }
    
    /**
     * Transfers data between Devices (e.g. multi-GPU).
     */
    static void deviceToDevice(void* d_dst, const void* d_src, size_t sizeBytes, cudaStream_t stream) {
        cudaError_t err = cudaMemcpyAsync(d_dst, d_src, sizeBytes, cudaMemcpyDeviceToDevice, stream);
        checkCudaError(err, "DeviceToDevice Async Memcpy");
    }

    /**
     * Blocks CPU until the specified stream completes its transfers.
     */
    static void synchronizeStream(cudaStream_t stream) {
        cudaError_t err = cudaStreamSynchronize(stream);
        checkCudaError(err, "Stream Synchronize");
    }
};
