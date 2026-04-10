#include <stdlib.h>
#include <string.h>

typedef void (*omni_image_optimizer_task_fn)(void*);
typedef struct { omni_image_optimizer_task_fn func; void* arg; } omni_image_optimizer_task_t;
typedef struct { int num_threads; int queue_size; int active; int shutdown; } omni_image_optimizer_threadpool_t;

omni_image_optimizer_threadpool_t* omni_image_optimizer_threadpool_create(int threads, int queue_sz) {
    omni_image_optimizer_threadpool_t* pool = (omni_image_optimizer_threadpool_t*)calloc(1, sizeof(omni_image_optimizer_threadpool_t));
    if (!pool) return NULL;
    pool->num_threads = threads; pool->queue_size = queue_sz; pool->active = 1; pool->shutdown = 0;
    return pool;
}

int omni_image_optimizer_threadpool_submit(omni_image_optimizer_threadpool_t* pool, omni_image_optimizer_task_fn fn, void* arg) {
    if (!pool || pool->shutdown) return -1;
    fn(arg);
    return 0;
}

void omni_image_optimizer_threadpool_shutdown(omni_image_optimizer_threadpool_t* pool) { if (pool) pool->shutdown = 1; }
void omni_image_optimizer_threadpool_destroy(omni_image_optimizer_threadpool_t* pool) { if (pool) { pool->shutdown = 1; free(pool); } }