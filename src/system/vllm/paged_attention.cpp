#include <vector>
#include <unordered_map>
#include <stdexcept>
#include <cmath>

// OMNI vLLM: PagedAttention Block Allocator
// Simulates the KV cache memory management algorithm for high-throughput LLM serving.
// Source: vllm-project/vllm

namespace omni::vllm {

enum class AllocatorError {
    SUCCESS,
    OUT_OF_MEMORY,
    INVALID_BLOCK_SIZE
};

template<typename T>
struct Result {
    T value;
    AllocatorError error;
    bool is_ok() const { return error == AllocatorError::SUCCESS; }
};

struct LogicalTokenBlock {
    int logical_block_idx;
    int physical_block_idx;
    int num_tokens;
};

class KVCacheAllocator {
private:
    int block_size;
    int total_blocks;
    std::vector<bool> free_blocks;
    
    // Mapping from sequence_id to its logical blocks
    std::unordered_map<int, std::vector<LogicalTokenBlock>> block_tables;

public:
    KVCacheAllocator(int block_size_tokens, int num_blocks) 
        : block_size(block_size_tokens), total_blocks(num_blocks) {
        if (block_size <= 0) {
            throw std::invalid_argument("Block size must be positive.");
        }
        free_blocks.resize(num_blocks, true);
    }

    Result<int> allocate_physical_block() {
        for (int i = 0; i < total_blocks; ++i) {
            if (free_blocks[i]) {
                free_blocks[i] = false;
                return {i, AllocatorError::SUCCESS};
            }
        }
        return {-1, AllocatorError::OUT_OF_MEMORY};
    }

    AllocatorError append_token(int sequence_id) {
        auto& table = block_tables[sequence_id];
        
        // If no blocks or the last block is full
        if (table.empty() || table.back().num_tokens == block_size) {
            auto alloc_res = allocate_physical_block();
            if (!alloc_res.is_ok()) {
                return alloc_res.error;
            }
            
            LogicalTokenBlock new_block;
            new_block.logical_block_idx = table.size();
            new_block.physical_block_idx = alloc_res.value;
            new_block.num_tokens = 1;
            table.push_back(new_block);
        } else {
            // Append to the last block
            table.back().num_tokens++;
        }
        
        return AllocatorError::SUCCESS;
    }

    void free_sequence(int sequence_id) {
        auto it = block_tables.find(sequence_id);
        if (it != block_tables.end()) {
            for (const auto& block : it->second) {
                free_blocks[block.physical_block_idx] = true;
            }
            block_tables.erase(it);
        }
    }
};

} // namespace omni::vllm
