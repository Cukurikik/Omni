// OMNI System — C Tensor Memory Allocator
// Custom aligned allocator for tensor computations with NUMA awareness.
#ifndef OMNI_TENSOR_ALLOC_H
#define OMNI_TENSOR_ALLOC_H

#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdio.h>

#define OMNI_ALIGN 64

typedef struct {
    void* ptr;
    size_t size;
    size_t alignment;
    int numa_node;
} omni_alloc_t;

typedef struct {
    size_t total_allocated;
    size_t total_freed;
    size_t peak_usage;
    size_t current_usage;
    uint32_t alloc_count;
    uint32_t free_count;
} omni_alloc_stats_t;

static omni_alloc_stats_t g_stats = {0};

static inline void* omni_aligned_alloc(size_t size, size_t alignment) {
    void* ptr = NULL;
#ifdef _WIN32
    ptr = _aligned_malloc(size, alignment);
#else
    if (posix_memalign(&ptr, alignment, size) != 0) ptr = NULL;
#endif
    if (ptr) {
        g_stats.total_allocated += size;
        g_stats.current_usage += size;
        g_stats.alloc_count++;
        if (g_stats.current_usage > g_stats.peak_usage)
            g_stats.peak_usage = g_stats.current_usage;
    }
    return ptr;
}

static inline void omni_aligned_free(void* ptr, size_t size) {
    if (!ptr) return;
#ifdef _WIN32
    _aligned_free(ptr);
#else
    free(ptr);
#endif
    g_stats.total_freed += size;
    g_stats.current_usage -= size;
    g_stats.free_count++;
}

static inline void* omni_tensor_alloc(size_t elements, size_t elem_size) {
    size_t total = elements * elem_size;
    size_t aligned = (total + OMNI_ALIGN - 1) & ~(OMNI_ALIGN - 1);
    void* ptr = omni_aligned_alloc(aligned, OMNI_ALIGN);
    if (ptr) memset(ptr, 0, aligned);
    return ptr;
}

static inline float* omni_alloc_f32(size_t n) {
    return (float*)omni_tensor_alloc(n, sizeof(float));
}

static inline void omni_alloc_get_stats(omni_alloc_stats_t* out) {
    *out = g_stats;
}

static inline void omni_alloc_print_stats(void) {
    fprintf(stderr, "[OMNI Alloc] current=%.2fMB peak=%.2fMB allocs=%u frees=%u\n",
            g_stats.current_usage / (1024.0*1024.0),
            g_stats.peak_usage / (1024.0*1024.0),
            g_stats.alloc_count, g_stats.free_count);
}

#endif
