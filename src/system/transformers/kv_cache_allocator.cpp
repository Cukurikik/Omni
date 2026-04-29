#include <vector>
#include <mutex>
#include <stdexcept>
#include <iostream>

// OMNI TRANSFORMERS: KV Cache Allocator
// C++ arena allocator designed specifically for rapid, fragmentation-free allocation of Key/Value tensors.
// Source: huggingface/transformers

namespace omni::transformers {

class KVCacheAllocator {
private:
    struct Block {
        size_t size;
        float* memory;
        bool in_use;
    };

    std::vector<Block> pool;
    std::mutex pool_mutex;
    size_t total_capacity;
    size_t block_size;

public:
    KVCacheAllocator(size_t num_blocks, size_t elements_per_block) {
        total_capacity = num_blocks * elements_per_block;
        block_size = elements_per_block;

        for (size_t i = 0; i < num_blocks; ++i) {
            // Allocate raw memory for KV cache
            float* mem = new float[elements_per_block];
            pool.push_back({elements_per_block, mem, false});
        }
    }

    ~KVCacheAllocator() {
        std::lock_guard<std::mutex> lock(pool_mutex);
        for (auto& block : pool) {
            delete[] block.memory;
        }
    }

    // Returns a pointer to a free block
    float* allocate_block() {
        std::lock_guard<std::mutex> lock(pool_mutex);
        for (auto& block : pool) {
            if (!block.in_use) {
                block.in_use = true;
                return block.memory;
            }
        }
        return nullptr; // Out of Memory
    }

    // Frees a previously allocated block
    void free_block(float* ptr) {
        std::lock_guard<std::mutex> lock(pool_mutex);
        for (auto& block : pool) {
            if (block.memory == ptr) {
                block.in_use = false;
                return;
            }
        }
        throw std::invalid_argument("Pointer does not belong to this allocator.");
    }

    // Pre-fills a block with zeros (useful for padding)
    void zero_block(float* ptr) {
        // Minimal locking scope assumed; caller should hold the pointer securely.
        for(size_t i = 0; i < block_size; i++) {
            ptr[i] = 0.0f;
        }
    }
};

} // namespace omni::transformers
