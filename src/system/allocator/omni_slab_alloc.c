/*
 * omni_slab_alloc.c — High-Performance Slab Allocator
 * Layer: System / C
 *
 * Implements a true slab allocator for fast, cache-aligned allocations 
 * of fixed-size objects (e.g., network packets, matrix blocks).
 * Zero-mock, relies on mmap for backend memory.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>
#include <pthread.h>

#define OMNI_SLAB_SIZE (4 * 1024 * 1024) // 4MB per slab

typedef struct OmniSlabNode {
    struct OmniSlabNode* next;
} OmniSlabNode;

typedef struct OmniSlabCache {
    size_t object_size;
    size_t capacity;
    size_t free_count;
    void* memory_block;
    OmniSlabNode* free_list;
    pthread_mutex_t lock;
} OmniSlabCache;

/*
 * Initialize a slab cache for a specific object size.
 */
OmniSlabCache* omni_slab_create(size_t object_size) {
    if (object_size < sizeof(OmniSlabNode)) {
        object_size = sizeof(OmniSlabNode);
    }
    
    // Ensure alignment to 8 bytes
    object_size = (object_size + 7) & ~7;

    OmniSlabCache* cache = (OmniSlabCache*)malloc(sizeof(OmniSlabCache));
    if (!cache) return NULL;

    cache->object_size = object_size;
    cache->capacity = OMNI_SLAB_SIZE / object_size;
    cache->free_count = cache->capacity;

    // Map memory anonymously
    cache->memory_block = mmap(NULL, OMNI_SLAB_SIZE, PROT_READ | PROT_WRITE, 
                               MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
                               
    if (cache->memory_block == MAP_FAILED) {
        free(cache);
        return NULL;
    }

    pthread_mutex_init(&cache->lock, NULL);

    // Build the free list inside the mapped memory
    cache->free_list = (OmniSlabNode*)cache->memory_block;
    OmniSlabNode* current = cache->free_list;

    for (size_t i = 1; i < cache->capacity; ++i) {
        OmniSlabNode* next_node = (OmniSlabNode*)((char*)current + object_size);
        current->next = next_node;
        current = next_node;
    }
    current->next = NULL;

    return cache;
}

/*
 * Allocate an object from the slab cache.
 */
void* omni_slab_alloc(OmniSlabCache* cache) {
    if (!cache) return NULL;

    pthread_mutex_lock(&cache->lock);

    if (cache->free_list == NULL) {
        pthread_mutex_unlock(&cache->lock);
        return NULL; // Out of memory in this slab
    }

    OmniSlabNode* node = cache->free_list;
    cache->free_list = node->next;
    cache->free_count--;

    pthread_mutex_unlock(&cache->lock);
    
    memset(node, 0, cache->object_size);
    return (void*)node;
}

/*
 * Free an object back to the slab cache.
 */
void omni_slab_free(OmniSlabCache* cache, void* obj) {
    if (!cache || !obj) return;

    pthread_mutex_lock(&cache->lock);

    OmniSlabNode* node = (OmniSlabNode*)obj;
    node->next = cache->free_list;
    cache->free_list = node;
    cache->free_count++;

    pthread_mutex_unlock(&cache->lock);
}

/*
 * Destroy the slab cache and unmap memory.
 */
void omni_slab_destroy(OmniSlabCache* cache) {
    if (!cache) return;
    
    pthread_mutex_lock(&cache->lock);
    munmap(cache->memory_block, OMNI_SLAB_SIZE);
    pthread_mutex_unlock(&cache->lock);
    
    pthread_mutex_destroy(&cache->lock);
    free(cache);
}
