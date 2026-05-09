// omni_vram_defrag.cpp — VRAM Defragmentation Logic
// Layer: System / C++
//
// Background maintenance routine for the OmniVRAMPool. Periodically scans
// for memory fragmentation and coalesces free blocks to accommodate large tensors.

#include <iostream>
#include <vector>
#include <algorithm>
#include <mutex>

// Mock definitions reflecting the structure of omni_vram_pool.cpp
struct Block {
    void* ptr;
    size_t size;
    bool is_free;
};

class OmniVRAMDefragmenter {
private:
    std::vector<Block>& pool_blocks;
    std::mutex& pool_mutex;

public:
    OmniVRAMDefragmenter(std::vector<Block>& blocks, std::mutex& mtx) 
        : pool_blocks(blocks), pool_mutex(mtx) {}

    /**
     * Coalesces adjacent free blocks. 
     * Requires the pool lock to be held.
     */
    size_t run_defragmentation() {
        std::lock_guard<std::mutex> lock(pool_mutex);
        
        if (pool_blocks.size() <= 1) return 0;

        size_t bytes_reclaimed = 0;
        auto it = pool_blocks.begin();

        while (it != pool_blocks.end() && (it + 1) != pool_blocks.end()) {
            auto next = it + 1;
            
            // If both current and next blocks are free, merge them
            if (it->is_free && next->is_free) {
                // Ensure they are contiguous in memory before merging
                char* expected_next_ptr = static_cast<char*>(it->ptr) + it->size;
                
                if (next->ptr == expected_next_ptr) {
                    it->size += next->size;
                    bytes_reclaimed += next->size;
                    pool_blocks.erase(next);
                    
                    // Do not advance iterator, check the newly merged block 
                    // against the next one in the following iteration
                    continue;
                }
            }
            ++it;
        }

        return bytes_reclaimed;
    }

    /**
     * Calculates fragmentation ratio (0.0 to 1.0)
     */
    double calculate_fragmentation() {
        std::lock_guard<std::mutex> lock(pool_mutex);
        
        size_t largest_free_block = 0;
        size_t total_free_memory = 0;

        for (const auto& block : pool_blocks) {
            if (block.is_free) {
                total_free_memory += block.size;
                if (block.size > largest_free_block) {
                    largest_free_block = block.size;
                }
            }
        }

        if (total_free_memory == 0) return 0.0;

        // Fragmentation metric: 1 - (largest_free_block / total_free_memory)
        // 0.0 means all free memory is in one block.
        // Higher values mean free memory is split across many small blocks.
        return 1.0 - (static_cast<double>(largest_free_block) / static_cast<double>(total_free_memory));
    }
};
