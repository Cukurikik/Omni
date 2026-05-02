/* @omni-domain System Layer (LatentMAS Memory)
   @omni-source various/latentmas
   @omni-description LatentMAS Memory mimicking latent agent state buffers in C.
   @omni-requirement zero-mock, monadic-error */
#include <stdlib.h>
#include <string.h>
typedef struct { void* data; char* error; int is_ok; } OmniResult;
typedef struct { double* buffer; int capacity; int used; } LatentMemoryPool;

OmniResult latent_pool_init(LatentMemoryPool* pool, int capacity) {
    OmniResult r;
    if (capacity <= 0) { r.data=NULL; r.error="Capacity must be > 0."; r.is_ok=0; return r; }
    pool->buffer = (double*)calloc(capacity, sizeof(double));
    if (!pool->buffer) { r.data=NULL; r.error="Alloc failed."; r.is_ok=0; return r; }
    pool->capacity = capacity;
    pool->used = 0;
    r.data=pool; r.error=NULL; r.is_ok=1; return r;
}

OmniResult latent_pool_store(LatentMemoryPool* pool, double* data, int len) {
    OmniResult r;
    if (!pool || !data) { r.data=NULL; r.error="Null args."; r.is_ok=0; return r; }
    if (pool->used + len > pool->capacity) { r.data=NULL; r.error="Pool overflow."; r.is_ok=0; return r; }
    memcpy(pool->buffer + pool->used, data, len * sizeof(double));
    pool->used += len;
    r.data=pool; r.error=NULL; r.is_ok=1; return r;
}

void latent_pool_free(LatentMemoryPool* pool) {
    if (pool && pool->buffer) { free(pool->buffer); pool->buffer = NULL; }
}
