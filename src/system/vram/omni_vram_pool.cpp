// omni_vram_pool.cpp — GPU VRAM Memory Pool
// Layer: System / C++
//
// Reduces CUDA allocation overhead by pre-allocating large chunks of VRAM
// and sub-allocating tensors from this pool dynamically.

#include <iostream>
#include <vector>
#include <mutex>
#include <cstdint>
#include <stdexcept>
#include <cuda_runtime.h>

class OmniVRAMPool {
private:
    struct Block {
        void* ptr;
        size_t size;
        bool is_free;
    };

    void* base_ptr;
    size_t total_size;
    std::vector<Block> blocks;
    std::mutex pool_mutex;

public:
    OmniVRAMPool(size_t size_in_bytes) : total_size(size_in_bytes) {
        cudaError_t err = cudaMalloc(&base_ptr, total_size);
        if (err != cudaSuccess) {
            throw std::runtime_error("Failed to allocate VRAM pool: " + std::string(cudaGetErrorString(err)));
        }
        
        blocks.push_back({base_ptr, total_size, true});
    }

    ~OmniVRAMPool() {
        cudaFree(base_ptr);
    }

    void* allocate(size_t size) {
        std::lock_guard<std::mutex> lock(pool_mutex);
        
        // Alignment to 256 bytes (common CUDA requirement)
        size_t aligned_size = (size + 255) & ~255;

        for (auto it = blocks.begin(); it != blocks.end(); ++it) {
            if (it->is_free && it->size >= aligned_size) {
                // Found a suitable block
                void* alloc_ptr = it->ptr;
                it->is_free = false;
                
                // Split block if there's enough remainder
                size_t remainder = it->size - aligned_size;
                if (remainder > 1024) { // Don't split for tiny fragments
                    it->size = aligned_size;
                    
                    Block new_block;
                    new_block.ptr = static_cast<char*>(alloc_ptr) + aligned_size;
                    new_block.size = remainder;
                    new_block.is_free = true;
                    
                    blocks.insert(it + 1, new_block);
                }
                
                return alloc_ptr;
            }
        }
        throw std::runtime_error("VRAM Pool out of memory");
    }

    void free(void* ptr) {
        std::lock_guard<std::mutex> lock(pool_mutex);
        
        for (auto it = blocks.begin(); it != blocks.end(); ++it) {
            if (it->ptr == ptr) {
                if (it->is_free) {
                    throw std::runtime_error("Double free in VRAM pool");
                }
                it->is_free = true;
                
                // Coalesce adjacent free blocks (simplified)
                if (it != blocks.begin()) {
                    auto prev = it - 1;
                    if (prev->is_free) {
                        prev->size += it->size;
                        blocks.erase(it);
                        it = prev;
                    }
                }
                
                if (it + 1 != blocks.end()) {
                    auto next = it + 1;
                    if (next->is_free) {
                        it->size += next->size;
                        blocks.erase(next);
                    }
                }
                return;
            }
        }
        throw std::runtime_error("Invalid pointer freed to VRAM pool");
    }
};
