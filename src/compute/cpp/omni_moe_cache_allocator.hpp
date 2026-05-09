#ifndef OMNI_MOE_CACHE_ALLOCATOR_HPP
#define OMNI_MOE_CACHE_ALLOCATOR_HPP

#include <vector>

namespace omni {
namespace compute {

/**
 * OMNI Framework - Paged KV Cache Allocator (C++)
 * Manages the physical memory blocks on the GPU for the PagedAttention system.
 * Designed to eliminate fragmentation and OOM errors during concurrent inference.
 */
class CacheAllocator {
public:
    CacheAllocator(int num_blocks, int block_size);
    ~CacheAllocator();

    // Allocates a physical block to a sequence
    int allocate();

    // Frees a physical block back to the pool
    void free(int block_id);

private:
    int num_blocks_;
    int block_size_;
    std::vector<int> free_list_;
};

} // namespace compute
} // namespace omni

#endif // OMNI_MOE_CACHE_ALLOCATOR_HPP
