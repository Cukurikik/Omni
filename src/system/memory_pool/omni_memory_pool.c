// omni_memory_pool.c — Custom Memory Pool Allocator
// Inspired by: jemalloc/tcmalloc slab allocation for OMNI inference
// Layer: System / C
//
// Fixed-size slab allocator for tensor buffers with
// free-list management and alignment guarantees.

#ifndef OMNI_MEMORY_POOL_H
#define OMNI_MEMORY_POOL_H

#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#ifdef _WIN32
#include <malloc.h>
#define omni_aligned_alloc(align, size) _aligned_malloc(size, align)
#define omni_aligned_free(ptr) _aligned_free(ptr)
#else
#include <stdalign.h>
#define omni_aligned_alloc(align, size) aligned_alloc(align, size)
#define omni_aligned_free(ptr) free(ptr)
#endif

#define OMNI_CACHE_LINE 64
#define OMNI_MAX_SLAB_CLASSES 16
#define OMNI_PAGE_SIZE 4096

typedef struct omni_free_node {
    struct omni_free_node* next;
} omni_free_node_t;

typedef struct omni_slab {
    struct omni_slab* next;
    uint8_t* base;           // Start of slab memory
    size_t object_size;      // Size of each object
    size_t capacity;         // Total objects in slab
    size_t allocated;        // Currently allocated count
    omni_free_node_t* free_list;
} omni_slab_t;

typedef struct omni_slab_class {
    size_t object_size;      // Aligned object size for this class
    size_t slab_size;        // Total bytes per slab
    omni_slab_t* active_slab;
    omni_slab_t* full_slabs;
    uint64_t total_allocs;
    uint64_t total_frees;
} omni_slab_class_t;

typedef struct omni_pool {
    omni_slab_class_t classes[OMNI_MAX_SLAB_CLASSES];
    int num_classes;
    size_t alignment;
    size_t total_memory;
    size_t peak_memory;
    bool initialized;
} omni_pool_t;

// === Pool Lifecycle ===

static inline size_t omni_align_up(size_t size, size_t alignment) {
    return (size + alignment - 1) & ~(alignment - 1);
}

int omni_pool_init(omni_pool_t* pool, size_t alignment) {
    if (!pool) return -1;

    memset(pool, 0, sizeof(omni_pool_t));
    pool->alignment = alignment > 0 ? alignment : OMNI_CACHE_LINE;
    pool->initialized = true;

    // Define slab size classes: 64B, 128B, 256B, ... 2MB
    size_t sizes[] = {64, 128, 256, 512, 1024, 2048, 4096,
                      8192, 16384, 32768, 65536, 131072,
                      262144, 524288, 1048576, 2097152};

    pool->num_classes = OMNI_MAX_SLAB_CLASSES;
    for (int i = 0; i < pool->num_classes; i++) {
        pool->classes[i].object_size = omni_align_up(sizes[i], pool->alignment);
        pool->classes[i].slab_size = sizes[i] < 4096 ? 65536 : sizes[i] * 16;
        pool->classes[i].active_slab = NULL;
        pool->classes[i].full_slabs = NULL;
        pool->classes[i].total_allocs = 0;
        pool->classes[i].total_frees = 0;
    }

    return 0;
}

// === Slab Management ===

static omni_slab_t* omni_slab_create(size_t object_size, size_t slab_size,
                                      size_t alignment) {
    omni_slab_t* slab = (omni_slab_t*)malloc(sizeof(omni_slab_t));
    if (!slab) return NULL;

    slab->base = (uint8_t*)omni_aligned_alloc(alignment, slab_size);
    if (!slab->base) {
        free(slab);
        return NULL;
    }

    slab->object_size = object_size;
    slab->capacity = slab_size / object_size;
    slab->allocated = 0;
    slab->next = NULL;

    // Build free list
    slab->free_list = NULL;
    for (size_t i = 0; i < slab->capacity; i++) {
        omni_free_node_t* node = (omni_free_node_t*)(slab->base + i * object_size);
        node->next = slab->free_list;
        slab->free_list = node;
    }

    return slab;
}

static void omni_slab_destroy(omni_slab_t* slab) {
    if (slab) {
        if (slab->base) {
            omni_aligned_free(slab->base);
        }
        free(slab);
    }
}

// === Class Selection ===

static int omni_find_class(omni_pool_t* pool, size_t size) {
    for (int i = 0; i < pool->num_classes; i++) {
        if (pool->classes[i].object_size >= size) {
            return i;
        }
    }
    return -1;  // Too large for pool
}

// === Allocation ===

void* omni_pool_alloc(omni_pool_t* pool, size_t size) {
    if (!pool || !pool->initialized || size == 0) return NULL;

    int class_idx = omni_find_class(pool, size);
    if (class_idx < 0) {
        // Fall back to system allocator for oversized requests
        return omni_aligned_alloc(pool->alignment, omni_align_up(size, pool->alignment));
    }

    omni_slab_class_t* cls = &pool->classes[class_idx];

    // Allocate new slab if needed
    if (!cls->active_slab || !cls->active_slab->free_list) {
        omni_slab_t* new_slab = omni_slab_create(
            cls->object_size, cls->slab_size, pool->alignment);
        if (!new_slab) return NULL;

        // Move full slab to full list
        if (cls->active_slab) {
            cls->active_slab->next = cls->full_slabs;
            cls->full_slabs = cls->active_slab;
        }

        cls->active_slab = new_slab;
        pool->total_memory += cls->slab_size;
        if (pool->total_memory > pool->peak_memory) {
            pool->peak_memory = pool->total_memory;
        }
    }

    // Pop from free list
    omni_free_node_t* node = cls->active_slab->free_list;
    cls->active_slab->free_list = node->next;
    cls->active_slab->allocated++;
    cls->total_allocs++;

    // Zero out the memory
    memset(node, 0, cls->object_size);
    return (void*)node;
}

// === Deallocation ===

static bool omni_slab_owns(omni_slab_t* slab, void* ptr) {
    uint8_t* p = (uint8_t*)ptr;
    return p >= slab->base && p < slab->base + slab->capacity * slab->object_size;
}

void omni_pool_free(omni_pool_t* pool, void* ptr, size_t size) {
    if (!pool || !ptr) return;

    int class_idx = omni_find_class(pool, size);
    if (class_idx < 0) {
        omni_aligned_free(ptr);
        return;
    }

    omni_slab_class_t* cls = &pool->classes[class_idx];

    // Check active slab
    if (cls->active_slab && omni_slab_owns(cls->active_slab, ptr)) {
        omni_free_node_t* node = (omni_free_node_t*)ptr;
        node->next = cls->active_slab->free_list;
        cls->active_slab->free_list = node;
        cls->active_slab->allocated--;
        cls->total_frees++;
        return;
    }

    // Check full slabs
    omni_slab_t* slab = cls->full_slabs;
    while (slab) {
        if (omni_slab_owns(slab, ptr)) {
            omni_free_node_t* node = (omni_free_node_t*)ptr;
            node->next = slab->free_list;
            slab->free_list = node;
            slab->allocated--;
            cls->total_frees++;
            return;
        }
        slab = slab->next;
    }
}

// === Statistics ===

typedef struct omni_pool_stats {
    size_t total_memory;
    size_t peak_memory;
    uint64_t total_allocs;
    uint64_t total_frees;
    int num_active_slabs;
    int num_full_slabs;
} omni_pool_stats_t;

omni_pool_stats_t omni_pool_get_stats(omni_pool_t* pool) {
    omni_pool_stats_t stats = {0};
    if (!pool) return stats;

    stats.total_memory = pool->total_memory;
    stats.peak_memory = pool->peak_memory;

    for (int i = 0; i < pool->num_classes; i++) {
        stats.total_allocs += pool->classes[i].total_allocs;
        stats.total_frees += pool->classes[i].total_frees;
        if (pool->classes[i].active_slab) stats.num_active_slabs++;

        omni_slab_t* slab = pool->classes[i].full_slabs;
        while (slab) {
            stats.num_full_slabs++;
            slab = slab->next;
        }
    }

    return stats;
}

// === Cleanup ===

void omni_pool_destroy(omni_pool_t* pool) {
    if (!pool) return;

    for (int i = 0; i < pool->num_classes; i++) {
        omni_slab_destroy(pool->classes[i].active_slab);

        omni_slab_t* slab = pool->classes[i].full_slabs;
        while (slab) {
            omni_slab_t* next = slab->next;
            omni_slab_destroy(slab);
            slab = next;
        }
    }

    pool->initialized = false;
}

#endif // OMNI_MEMORY_POOL_H
