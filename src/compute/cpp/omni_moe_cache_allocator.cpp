#include "omni_moe_cache_allocator.hpp"
#include <iostream>

namespace omni {
namespace compute {

CacheAllocator::CacheAllocator(int num_blocks, int block_size) 
    : num_blocks_(num_blocks), block_size_(block_size) {
    
    std::cout << "OMNI C++: Initializing Paged KV Cache Allocator (" 
              << num_blocks << " blocks, " << block_size << " elements/block)." << std::endl;
              
    for (int i = 0; i < num_blocks; ++i) {
        free_list_.push_back(i);
    }
}

CacheAllocator::~CacheAllocator() {
    std::cout << "OMNI C++: Destroying Cache Allocator." << std::endl;
}

int CacheAllocator::allocate() {
    if (free_list_.empty()) {
        std::cerr << "OMNI C++: ERROR - KV Cache OOM! No free blocks available." << std::endl;
        return -1; // Trigger Eviction or Panic
    }
    
    int block_id = free_list_.back();
    free_list_.pop_back();
    return block_id;
}

void CacheAllocator::free(int block_id) {
    free_list_.push_back(block_id);
}

} // namespace compute
} // namespace omni
