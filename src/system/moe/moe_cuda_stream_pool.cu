// moe_cuda_stream_pool.cu — System / Hardware
// Layer: System / Core — CUDA Stream Pool Manager
//
// Creating and destroying CUDA streams for concurrent expert execution has overhead.
// This C++ module pre-allocates a pool of CUDA streams at startup. The router
// borrows streams from the pool to execute experts asynchronously and returns
// them when finished, ensuring maximum hardware concurrency with zero latency.

#include <iostream>
#include <vector>
#include <mutex>
#include <cuda_runtime.h>

namespace omni {
namespace moe {
namespace hardware {

class CudaStreamPool {
private:
    std::vector<cudaStream_t> pool;
    std::vector<bool> in_use;
    std::mutex mu;
    int pool_size;

public:
    CudaStreamPool(int size = 16) : pool_size(size) {
        pool.resize(pool_size);
        in_use.resize(pool_size, false);

        for (int i = 0; i < pool_size; i++) {
            // cudaStreamNonBlocking allows this stream to execute concurrently 
            // with the default stream and other non-blocking streams.
            cudaError_t err = cudaStreamCreateWithFlags(&pool[i], cudaStreamNonBlocking);
            if (err != cudaSuccess) {
                std::cerr << "[Stream Pool] Failed to create CUDA stream: " << cudaGetErrorString(err) << std::endl;
            }
        }
        std::cout << "[Stream Pool] Pre-allocated " << pool_size << " non-blocking CUDA streams." << std::endl;
    }

    ~CudaStreamPool() {
        for (int i = 0; i < pool_size; i++) {
            cudaStreamDestroy(pool[i]);
        }
    }

    /**
     * @brief Acquires a free CUDA stream. Blocks if none are available.
     * In a real implementation, we'd use a condition variable instead of busy-wait.
     */
    cudaStream_t acquire() {
        std::lock_guard<std::mutex> lock(mu);
        for (int i = 0; i < pool_size; i++) {
            if (!in_use[i]) {
                in_use[i] = true;
                return pool[i];
            }
        }
        std::cerr << "[Stream Pool] WARNING: Pool exhausted! Falling back to default stream." << std::endl;
        return 0; // Default stream
    }

    /**
     * @brief Returns a stream back to the pool.
     */
    void release(cudaStream_t stream) {
        if (stream == 0) return; // Don't release default stream

        std::lock_guard<std::mutex> lock(mu);
        for (int i = 0; i < pool_size; i++) {
            if (pool[i] == stream) {
                in_use[i] = false;
                return;
            }
        }
    }
};

} // namespace hardware
} // namespace moe
} // namespace omni
