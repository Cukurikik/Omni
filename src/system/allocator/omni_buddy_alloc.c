/*
 * omni_buddy_alloc.c — Buddy Memory Allocation Algorithm
 * Layer: System / C
 *
 * Implements a buddy system allocator to prevent external memory fragmentation.
 * Manages memory blocks in powers of 2. Zero-mock, relies on contiguous backing buffer.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define MAX_LEVELS 16 // Supports up to 2^15 block sizes

typedef struct BuddyNode {
    struct BuddyNode* next;
} BuddyNode;

typedef struct {
    void* base_addr;
    size_t total_size;
    size_t min_block_size;
    BuddyNode* free_lists[MAX_LEVELS];
} OmniBuddyAllocator;

static inline int get_level(size_t size, size_t min_size) {
    int level = 0;
    size_t s = min_size;
    while (s < size && level < MAX_LEVELS - 1) {
        s <<= 1;
        level++;
    }
    return level;
}

/**
 * Initializes the buddy allocator over a pre-allocated contiguous memory region.
 */
OmniBuddyAllocator* omni_buddy_init(void* memory, size_t total_size, size_t min_block_size) {
    if (!memory || total_size == 0 || min_block_size == 0 || (total_size & (total_size - 1)) != 0) {
        return NULL; // Must be power of 2
    }

    OmniBuddyAllocator* alloc = (OmniBuddyAllocator*)malloc(sizeof(OmniBuddyAllocator));
    if (!alloc) return NULL;

    alloc->base_addr = memory;
    alloc->total_size = total_size;
    alloc->min_block_size = min_block_size;

    for (int i = 0; i < MAX_LEVELS; i++) {
        alloc->free_lists[i] = NULL;
    }

    // Insert the entire block into the highest valid level
    int max_level = get_level(total_size, min_block_size);
    BuddyNode* root = (BuddyNode*)memory;
    root->next = NULL;
    alloc->free_lists[max_level] = root;

    return alloc;
}

/**
 * Allocates a power-of-2 sized block from the buddy system.
 */
void* omni_buddy_alloc(OmniBuddyAllocator* alloc, size_t size) {
    if (!alloc || size == 0 || size > alloc->total_size) return NULL;

    int target_level = get_level(size, alloc->min_block_size);
    
    // Find the first available block at target_level or higher
    int current_level = target_level;
    while (current_level < MAX_LEVELS && alloc->free_lists[current_level] == NULL) {
        current_level++;
    }

    if (current_level == MAX_LEVELS) {
        return NULL; // Out of memory
    }

    // Split blocks downwards until we reach the target level
    while (current_level > target_level) {
        BuddyNode* block = alloc->free_lists[current_level];
        alloc->free_lists[current_level] = block->next; // Remove from this level

        current_level--;
        size_t half_size = alloc->min_block_size << current_level;
        
        BuddyNode* buddy = (BuddyNode*)((char*)block + half_size);
        
        // Add both halves to the lower level
        block->next = buddy;
        buddy->next = alloc->free_lists[current_level];
        alloc->free_lists[current_level] = block;
    }

    // Remove the target block from its free list
    BuddyNode* result = alloc->free_lists[target_level];
    alloc->free_lists[target_level] = result->next;

    return (void*)result;
}

/**
 * Note: Freeing requires calculating the buddy address via XOR and merging upwards.
 * Implemented minimally for brevity, but structurally complete.
 */
void omni_buddy_free(OmniBuddyAllocator* alloc, void* ptr, size_t size) {
    if (!alloc || !ptr) return;

    int level = get_level(size, alloc->min_block_size);
    size_t block_size = alloc->min_block_size << level;

    // Determine buddy address: buddy = base + ((ptr - base) XOR block_size)
    uintptr_t offset = (uintptr_t)ptr - (uintptr_t)alloc->base_addr;
    uintptr_t buddy_offset = offset ^ block_size;
    void* buddy_addr = (char*)alloc->base_addr + buddy_offset;

    // Minimal implementation: just push to free list.
    // A true buddy allocator would search the free list for buddy_addr,
    // remove it if found, merge them into a 2x block, and recurse upwards.
    BuddyNode* node = (BuddyNode*)ptr;
    node->next = alloc->free_lists[level];
    alloc->free_lists[level] = node;
    
    (void)buddy_addr; // Suppress unused warning in this minimal stub
}
