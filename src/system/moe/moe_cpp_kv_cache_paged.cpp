// moe_cpp_kv_cache_paged.cpp — System / Memory
// Layer: System / Memory — PagedAttention KV Cache Manager
//
// Inspired by vLLM's PagedAttention.
// Storing KV caches in contiguous VRAM causes massive fragmentation when 
// dealing with concurrent requests of variable sequence lengths.
// This C++ module manages the KV Cache as a series of non-contiguous "pages" 
// (e.g., 16 tokens per block), dramatically reducing memory waste.

#include <iostream>
#include <vector>
#include <unordered_map>
#include <mutex>

namespace omni {
namespace moe {
namespace memory {

struct Block {
    int block_id;
    int current_tokens;
    int max_tokens; // e.g., 16
    bool is_free;
};

class PagedKVCacheManager {
private:
    std::vector<Block> physical_blocks;
    std::unordered_map<std::string, std::vector<int>> request_block_tables;
    std::mutex mu;
    int block_size;

public:
    PagedKVCacheManager(int total_blocks, int block_size = 16) 
        : block_size(block_size) {
        std::cout << "[Paged KV Cache] Initializing " << total_blocks << " memory blocks (Size: " << block_size << " tokens/block)." << std::endl;
        
        physical_blocks.reserve(total_blocks);
        for(int i = 0; i < total_blocks; i++) {
            physical_blocks.push_back({i, 0, block_size, true});
        }
    }

    /**
     * @brief Allocates a new physical block to a request ID.
     */
    int allocate_block(const std::string& request_id) {
        std::lock_guard<std::mutex> lock(mu);
        
        // Find first free block
        for(auto& block : physical_blocks) {
            if (block.is_free) {
                block.is_free = false;
                block.current_tokens = 0;
                
                request_block_tables[request_id].push_back(block.block_id);
                // std::cout << "[Paged KV Cache] Allocated Block " << block.block_id << " to Req " << request_id << std::endl;
                return block.block_id;
            }
        }
        
        std::cerr << "[Paged KV Cache] OUT OF MEMORY: No free KV blocks available!" << std::endl;
        return -1; // OOM
    }

    /**
     * @brief Frees all blocks associated with a finished request.
     */
    void free_request(const std::string& request_id) {
        std::lock_guard<std::mutex> lock(mu);
        
        auto it = request_block_tables.find(request_id);
        if (it != request_block_tables.end()) {
            int freed = 0;
            for(int block_id : it->second) {
                physical_blocks[block_id].is_free = true;
                physical_blocks[block_id].current_tokens = 0;
                freed++;
            }
            request_block_tables.erase(it);
            // std::cout << "[Paged KV Cache] Freed " << freed << " blocks for Req " << request_id << std::endl;
        }
    }
};

} // namespace memory
} // namespace moe
} // namespace omni
