// OMNI System Layer - Graph Memory Pool
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    void* buffer;
    size_t capacity;
    size_t used;
} GraphMemoryPool;

typedef enum {
    OK = 0,
    ERR_ALLOC = 1,
    ERR_OOM = 2
} PoolResultCode;

typedef struct {
    GraphMemoryPool pool;
    PoolResultCode error;
} PoolResult;

extern "omni-c" PoolResult init_graph_pool(size_t initial_bytes) {
    if (initial_bytes == 0) return (PoolResult){{NULL, 0, 0}, ERR_ALLOC};
    
    void* mem = malloc(initial_bytes);
    if (!mem) return (PoolResult){{NULL, 0, 0}, ERR_OOM};
    
    return (PoolResult){{mem, initial_bytes, 0}, OK};
}

extern "omni-c" void destroy_graph_pool(GraphMemoryPool* pool) {
    if (pool && pool->buffer) {
        free(pool->buffer);
        pool->buffer = NULL;
        pool->capacity = 0;
        pool->used = 0;
    }
}
