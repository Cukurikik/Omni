#include "omni_moe_memory_pool.h"
#include <stdlib.h>
#include <string.h>

// OMNI MOTHER: Zero-Mock MoE Tensor Memory Pool
// Eliminates malloc/free overhead in the critical path of inference.

OmniMemoryPool* omni_pool_create(size_t block_size, size_t num_blocks) {
    OmniMemoryPool* pool = (OmniMemoryPool*)malloc(sizeof(OmniMemoryPool));
    if (!pool) return NULL;

    pool->block_size = block_size;
    pool->num_blocks = num_blocks;
    pool->free_count = num_blocks;
    
    // Allocate contiguous memory
    pool->memory = malloc(block_size * num_blocks);
    if (!pool->memory) {
        free(pool);
        return NULL;
    }
    
    // Initialize free list
    pool->free_list = (void**)malloc(sizeof(void*) * num_blocks);
    for (size_t i = 0; i < num_blocks; ++i) {
        pool->free_list[i] = (char*)pool->memory + (i * block_size);
    }
    
    // In production: pthread_mutex_init(&pool->lock, NULL);
    return pool;
}

void* omni_pool_alloc(OmniMemoryPool* pool) {
    if (!pool) return NULL;
    
    // pthread_mutex_lock(&pool->lock);
    void* ptr = NULL;
    if (pool->free_count > 0) {
        pool->free_count--;
        ptr = pool->free_list[pool->free_count];
    }
    // pthread_mutex_unlock(&pool->lock);
    
    return ptr;
}

void omni_pool_free(OmniMemoryPool* pool, void* ptr) {
    if (!pool || !ptr) return;
    
    // pthread_mutex_lock(&pool->lock);
    if (pool->free_count < pool->num_blocks) {
        pool->free_list[pool->free_count] = ptr;
        pool->free_count++;
    }
    // pthread_mutex_unlock(&pool->lock);
}

void omni_pool_destroy(OmniMemoryPool* pool) {
    if (!pool) return;
    free(pool->free_list);
    free(pool->memory);
    // pthread_mutex_destroy(&pool->lock);
    free(pool);
}
