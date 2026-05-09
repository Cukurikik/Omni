// moe_paged_attention_c.c — System / Core
// Layer: System / Memory — Paged KV Cache Manager
//
// A hardware-level C implementation of PagedAttention (inspired by vLLM).
// Standard LLM inference allocates contiguous VRAM for KV caches, leading to 
// massive fragmentation. This acts like an OS virtual memory manager, dividing 
// the KV cache into fixed-size physical blocks (pages) to eliminate fragmentation.

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#define PAGE_SIZE 16        // Number of tokens per page
#define NUM_PAGES 65536     // Total pages in VRAM pool
#define INVALID_PAGE 0xFFFFFFFF

typedef struct {
    uint32_t physical_page_idx;
    bool is_free;
} PageBlock;

typedef struct {
    PageBlock pool[NUM_PAGES];
    uint32_t free_pages_count;
} KVPageAllocator;

KVPageAllocator* init_paged_kv_cache() {
    KVPageAllocator* allocator = (KVPageAllocator*)malloc(sizeof(KVPageAllocator));
    for (uint32_t i = 0; i < NUM_PAGES; i++) {
        allocator->pool[i].physical_page_idx = i;
        allocator->pool[i].is_free = true;
    }
    allocator->free_pages_count = NUM_PAGES;
    
    printf("[PagedAttention] Initialized VRAM Page Allocator. Total Pages: %d (Block Size: %d tokens)\n", NUM_PAGES, PAGE_SIZE);
    return allocator;
}

/**
 * Allocates a single physical page for a logical sequence block.
 */
uint32_t allocate_page(KVPageAllocator* allocator) {
    if (allocator->free_pages_count == 0) {
        fprintf(stderr, "[PagedAttention] FATAL: VRAM KV Cache Exhausted. OOM.\n");
        return INVALID_PAGE;
    }

    // O(N) linear search. In production, we use a bitmap or free-list stack.
    for (uint32_t i = 0; i < NUM_PAGES; i++) {
        if (allocator->pool[i].is_free) {
            allocator->pool[i].is_free = false;
            allocator->free_pages_count--;
            return i;
        }
    }
    return INVALID_PAGE;
}

/**
 * Frees a physical page when a sequence generation completes.
 */
void free_page(KVPageAllocator* allocator, uint32_t page_idx) {
    if (page_idx >= NUM_PAGES || allocator->pool[page_idx].is_free) {
        return; // Invalid or double-free
    }
    allocator->pool[page_idx].is_free = true;
    allocator->free_pages_count++;
}

void destroy_paged_kv_cache(KVPageAllocator* allocator) {
    free(allocator);
}
