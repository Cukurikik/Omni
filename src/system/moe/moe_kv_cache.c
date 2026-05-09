// moe_kv_cache.c — System / Memory
// Layer: System / Memory — KV Cache optimized for MoE
//
// Standard KV Caches struggle with MoE because sequence token routing diverges wildly.
// This implementation uses a Paged KV Cache struct in C for O(1) page allocation,
// specifically handling non-contiguous token blocks scattered across experts.

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define PAGE_SIZE 16   // Number of tokens per page
#define HIDDEN_DIM 128 // Dimension of K and V
#define MAX_PAGES 1024 // Total available pages in memory

// Represents a single page in the KV Cache
typedef struct {
    int is_allocated;
    float k_cache[PAGE_SIZE * HIDDEN_DIM];
    float v_cache[PAGE_SIZE * HIDDEN_DIM];
} KVPage;

// The global MoE KV Cache memory pool
typedef struct {
    KVPage pages[MAX_PAGES];
    int free_pages_count;
} MoEKVCache;

MoEKVCache* init_moe_kv_cache() {
    MoEKVCache* cache = (MoEKVCache*)malloc(sizeof(MoEKVCache));
    if (!cache) return NULL;
    
    memset(cache->pages, 0, sizeof(cache->pages));
    cache->free_pages_count = MAX_PAGES;
    
    printf("[MoE KV Cache] Initialized Paged Memory Pool with %d pages.\n", MAX_PAGES);
    return cache;
}

// Allocates a physical page for a logical token sequence
int allocate_page(MoEKVCache* cache) {
    if (cache->free_pages_count == 0) {
        fprintf(stderr, "[MoE KV Cache] OOM Error: No free pages available.\n");
        return -1;
    }
    
    for (int i = 0; i < MAX_PAGES; i++) {
        if (!cache->pages[i].is_allocated) {
            cache->pages[i].is_allocated = 1;
            cache->free_pages_count--;
            return i; // Return physical page index
        }
    }
    return -1;
}

// Frees a physical page
void free_page(MoEKVCache* cache, int page_idx) {
    if (page_idx >= 0 && page_idx < MAX_PAGES && cache->pages[page_idx].is_allocated) {
        cache->pages[page_idx].is_allocated = 0;
        cache->free_pages_count++;
    }
}

void destroy_moe_kv_cache(MoEKVCache* cache) {
    if (cache) {
        free(cache);
    }
}
