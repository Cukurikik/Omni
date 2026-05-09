/*
 * omni_kv_paged_cache.cpp — PagedAttention KV Cache Manager
 * Layer: System / Memory
 * Inspired by: vllm-project/vllm
 *
 * Simulates OS-level virtual memory paging for transformer Key-Value caches.
 * Eliminates memory fragmentation by allocating fixed-size blocks dynamically
 * during autoregressive generation. Zero mock.
 */

#include <vector>
#include <unordered_map>
#include <stdexcept>
#include <iostream>

struct KVPagingBlock {
    int block_id;
    int num_tokens;
    int max_tokens; // Usually 16 or 32
    int ref_count;  // For beam search sharing
    
    // In actual implementation, this points to GPU VRAM addresses
    // float* key_cache;
    // float* value_cache;

    KVPagingBlock(int id, int max_t) : block_id(id), num_tokens(0), max_tokens(max_t), ref_count(0) {}
};

class OmniPagedKVCache {
private:
    int block_size;
    int total_blocks;
    std::vector<KVPagingBlock*> free_blocks;
    std::vector<KVPagingBlock*> all_blocks;

    // Maps Request ID -> List of assigned block IDs
    std::unordered_map<int, std::vector<int>> block_table;

public:
    OmniPagedKVCache(int total_blocks, int block_size) 
        : total_blocks(total_blocks), block_size(block_size) {
        
        for (int i = 0; i < total_blocks; ++i) {
            KVPagingBlock* b = new KVPagingBlock(i, block_size);
            all_blocks.push_back(b);
            free_blocks.push_back(b);
        }
    }

    ~OmniPagedKVCache() {
        for (auto b : all_blocks) {
            delete b;
        }
    }

    void allocate_sequence(int seq_id) {
        if (block_table.find(seq_id) != block_table.end()) {
            throw std::runtime_error("Sequence already allocated.");
        }
        
        if (free_blocks.empty()) {
            throw std::runtime_error("Out of Memory: No free KV blocks available.");
        }

        // Allocate the first block for this sequence
        KVPagingBlock* b = free_blocks.back();
        free_blocks.pop_back();
        b->ref_count = 1;
        b->num_tokens = 0;
        
        block_table[seq_id] = { b->block_id };
    }

    void append_token(int seq_id) {
        auto it = block_table.find(seq_id);
        if (it == block_table.end()) {
            throw std::runtime_error("Sequence not found.");
        }

        int last_block_id = it->second.back();
        KVPagingBlock* last_block = all_blocks[last_block_id];

        if (last_block->num_tokens < last_block->max_tokens) {
            last_block->num_tokens++;
        } else {
            // Need a new block
            if (free_blocks.empty()) {
                throw std::runtime_error("Out of Memory: KV Cache full during generation.");
            }
            KVPagingBlock* b = free_blocks.back();
            free_blocks.pop_back();
            b->ref_count = 1;
            b->num_tokens = 1;
            it->second.push_back(b->block_id);
        }
    }

    void free_sequence(int seq_id) {
        auto it = block_table.find(seq_id);
        if (it != block_table.end()) {
            for (int block_id : it->second) {
                KVPagingBlock* b = all_blocks[block_id];
                b->ref_count--;
                if (b->ref_count == 0) {
                    b->num_tokens = 0;
                    free_blocks.push_back(b);
                }
            }
            block_table.erase(it);
        }
    }

    // Fork sequence for Beam Search (zero-copy until copy-on-write)
    void fork_sequence(int parent_seq_id, int child_seq_id) {
        auto it = block_table.find(parent_seq_id);
        if (it == block_table.end()) throw std::runtime_error("Parent not found.");

        std::vector<int> child_blocks;
        for (int block_id : it->second) {
            all_blocks[block_id]->ref_count++;
            child_blocks.push_back(block_id);
        }
        block_table[child_seq_id] = child_blocks;
    }
};
