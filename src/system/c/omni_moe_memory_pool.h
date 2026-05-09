#ifndef OMNI_MOE_MEMORY_POOL_H
#define OMNI_MOE_MEMORY_POOL_H

#include <stddef.h>
// #include <pthread.h> // For production mutex

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    size_t block_size;
    size_t num_blocks;
    size_t free_count;
    void* memory;
    void** free_list;
    // pthread_mutex_t lock;
} OmniMemoryPool;

OmniMemoryPool* omni_pool_create(size_t block_size, size_t num_blocks);
void* omni_pool_alloc(OmniMemoryPool* pool);
void omni_pool_free(OmniMemoryPool* pool, void* ptr);
void omni_pool_destroy(OmniMemoryPool* pool);

#ifdef __cplusplus
}
#endif

#endif // OMNI_MOE_MEMORY_POOL_H
