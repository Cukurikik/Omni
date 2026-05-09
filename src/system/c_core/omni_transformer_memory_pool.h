#ifndef OMNI_TRANSFORMER_MEMORY_POOL_H
#define OMNI_TRANSFORMER_MEMORY_POOL_H

#include <stddef.h>
#include <stdint.h>

/*
 * OMNI Framework - Transformer Memory Pool
 * Custom C memory allocator for zero-copy tensor allocations 
 * during transformer inference to prevent fragmentation.
 */

typedef struct OmniMemPool OmniMemPool;

/* Initialize a memory pool with a specific size in bytes */
OmniMemPool* omni_mempool_create(size_t pool_size);

/* Allocate a block of memory from the pool */
void* omni_mempool_alloc(OmniMemPool* pool, size_t size, size_t alignment);

/* Free all allocations in the pool (bump allocator logic) */
void omni_mempool_reset(OmniMemPool* pool);

/* Destroy the memory pool */
void omni_mempool_destroy(OmniMemPool* pool);

#endif // OMNI_TRANSFORMER_MEMORY_POOL_H
