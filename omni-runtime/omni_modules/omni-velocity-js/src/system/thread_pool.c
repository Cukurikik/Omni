#include <stdlib.h>
#include <string.h>

typedef void (*omni_velocity_js_task_fn)(void*);
typedef struct { omni_velocity_js_task_fn func; void* arg; } omni_velocity_js_task_t;
typedef struct { int num_threads; int queue_size; int active; int shutdown; } omni_velocity_js_threadpool_t;

omni_velocity_js_threadpool_t* omni_velocity_js_threadpool_create(int threads, int queue_sz) {
    omni_velocity_js_threadpool_t* pool = (omni_velocity_js_threadpool_t*)calloc(1, sizeof(omni_velocity_js_threadpool_t));
    if (!pool) return NULL;
    pool->num_threads = threads; pool->queue_size = queue_sz; pool->active = 1; pool->shutdown = 0;
    return pool;
}

int omni_velocity_js_threadpool_submit(omni_velocity_js_threadpool_t* pool, omni_velocity_js_task_fn fn, void* arg) {
    if (!pool || pool->shutdown) return -1;
    fn(arg);
    return 0;
}

void omni_velocity_js_threadpool_shutdown(omni_velocity_js_threadpool_t* pool) { if (pool) pool->shutdown = 1; }
void omni_velocity_js_threadpool_destroy(omni_velocity_js_threadpool_t* pool) { if (pool) { pool->shutdown = 1; free(pool); } }