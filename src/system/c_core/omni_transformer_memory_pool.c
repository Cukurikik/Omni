#include "omni_transformer_memory_pool.h"
#include <stdlib.h>
#include <string.h>

struct OmniMemPool {
    uint8_t* buffer;
    size_t capacity;
    size_t offset;
};

OmniMemPool* omni_mempool_create(size_t pool_size) {
    OmniMemPool* pool = (OmniMemPool*)malloc(sizeof(OmniMemPool));
    if (!pool) return NULL;

    pool->buffer = (uint8_t*)malloc(pool_size);
    if (!pool->buffer) {
        free(pool);
        return NULL;
    }

    pool->capacity = pool_size;
    pool->offset = 0;
    return pool;
}

void* omni_mempool_alloc(OmniMemPool* pool, size_t size, size_t alignment) {
    if (!pool) return NULL;

    // Calculate alignment offset
    size_t remainder = pool->offset % alignment;
    size_t align_offset = remainder == 0 ? 0 : alignment - remainder;
    
    if (pool->offset + align_offset + size > pool->capacity) {
        // Out of memory in this pool
        return NULL;
    }

    pool->offset += align_offset;
    void* ptr = pool->buffer + pool->offset;
    pool->offset += size;

    return ptr;
}

void omni_mempool_reset(OmniMemPool* pool) {
    if (pool) {
        pool->offset = 0;
    }
}

void omni_mempool_destroy(OmniMemPool* pool) {
    if (pool) {
        if (pool->buffer) {
            free(pool->buffer);
        }
        free(pool);
    }
}
