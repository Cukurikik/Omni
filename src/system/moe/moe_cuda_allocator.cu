// moe_cuda_allocator.cu — System / Hardware
// Layer: System / Memory — Custom CUDA VRAM Pool
//
// A custom memory allocator specifically designed for the rapid, dynamic allocation 
// and deallocation of variable-sized MoE expert activations during inference.
// Prevents cudaMalloc fragmentation by maintaining pre-allocated blocks.

#include <iostream>
#include <vector>
#include <cuda_runtime.h>
#include <mutex>

namespace omni {
namespace moe {
namespace memory {

#define CHUNK_SIZE_MB 256
#define BYTES_PER_MB (1024 * 1024)

class MoEActivationPool {
private:
    void* base_pointer;
    size_t total_capacity_bytes;
    size_t currently_used_bytes;
    std::mutex pool_mutex;

    void checkCuda(cudaError_t result, const char* msg) {
        if (result != cudaSuccess) {
            std::cerr << "[CUDA Pool] Error: " << msg << " - " << cudaGetErrorString(result) << std::endl;
            exit(1);
        }
    }

public:
    MoEActivationPool(size_t max_capacity_mb) {
        total_capacity_bytes = max_capacity_mb * BYTES_PER_MB;
        currently_used_bytes = 0;
        
        std::cout << "[CUDA Pool] Pre-allocating " << max_capacity_mb << " MB for MoE activations..." << std::endl;
        checkCuda(cudaMalloc(&base_pointer, total_capacity_bytes), "cudaMalloc Pool Base");
    }

    ~MoEActivationPool() {
        cudaFree(base_pointer);
    }

    /**
     * @brief Allocates a chunk of VRAM sequentially from the pool.
     * In a production environment, this is a slab allocator. Here, we use
     * a simple bump allocator for zero-mock compilation.
     */
    void* allocate_activation_space(size_t size_bytes) {
        std::lock_guard<std::mutex> lock(pool_mutex);
        
        // 256-byte alignment
        size_t aligned_size = (size_bytes + 255) & ~255;
        
        if (currently_used_bytes + aligned_size > total_capacity_bytes) {
            std::cerr << "[CUDA Pool] OOM Error: Failed to allocate " << aligned_size 
                      << " bytes. Pool exhausted." << std::endl;
            return nullptr;
        }

        void* alloc_ptr = static_cast<char*>(base_pointer) + currently_used_bytes;
        currently_used_bytes += aligned_size;
        
        return alloc_ptr;
    }

    /**
     * @brief Resets the bump allocator. 
     * Designed to be called at the end of every forward pass layer.
     */
    void reset_for_next_layer() {
        std::lock_guard<std::mutex> lock(pool_mutex);
        currently_used_bytes = 0;
    }
    
    size_t get_utilization_bytes() {
        return currently_used_bytes;
    }
};

} // namespace memory
} // namespace moe
} // namespace omni
