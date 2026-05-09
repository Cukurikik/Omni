/**
 * OMNI MOTHER: C Kernel Bridge (Production Grade)
 * Provides zero-copy memory management, aligned allocation, ring buffers,
 * and secure memory operations for the OMNI kernel FFI boundary.
 */
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>
#include <stdalign.h>

/* ---- Aligned Allocation ---- */

void* omni_sys_malloc_aligned(size_t size, size_t alignment) {
    if (size == 0 || alignment == 0 || (alignment & (alignment - 1)) != 0) {
        return NULL; /* alignment must be power of 2 */
    }
#ifdef _WIN32
    void* ptr = _aligned_malloc(size, alignment);
#else
    void* ptr = NULL;
    if (posix_memalign(&ptr, alignment, size) != 0) {
        return NULL;
    }
#endif
    if (ptr) memset(ptr, 0, size);
    return ptr;
}

void omni_sys_free_aligned(void* ptr) {
#ifdef _WIN32
    _aligned_free(ptr);
#else
    free(ptr);
#endif
}

/* ---- Zero-Init Allocation ---- */

void* omni_sys_malloc(size_t size) {
    if (size == 0) return NULL;
    void* ptr = malloc(size);
    if (ptr) memset(ptr, 0, size);
    return ptr;
}

void omni_sys_free(void* ptr) {
    if (ptr) free(ptr);
}

/* ---- Secure Memory Wipe ---- */

void omni_secure_zero(void* ptr, size_t size) {
    if (!ptr || size == 0) return;
    volatile uint8_t* p = (volatile uint8_t*)ptr;
    for (size_t i = 0; i < size; i++) {
        p[i] = 0;
    }
}

/* ---- Fast Memory Copy with Overlap Check ---- */

int omni_fast_memory_copy(void* dest, const void* src, size_t n) {
    if (!dest || !src || n == 0) return -1;
    /* Use memmove for safety (handles overlap) */
    memmove(dest, src, n);
    return 0;
}

/* ---- Ring Buffer for Zero-Copy IPC ---- */

typedef struct {
    uint8_t* buffer;
    size_t   capacity;
    size_t   read_pos;
    size_t   write_pos;
    size_t   count;
} OmniRingBuffer;

OmniRingBuffer* omni_ring_create(size_t capacity) {
    if (capacity == 0) return NULL;
    OmniRingBuffer* rb = (OmniRingBuffer*)omni_sys_malloc(sizeof(OmniRingBuffer));
    if (!rb) return NULL;
    rb->buffer = (uint8_t*)omni_sys_malloc(capacity);
    if (!rb->buffer) {
        free(rb);
        return NULL;
    }
    rb->capacity = capacity;
    rb->read_pos = 0;
    rb->write_pos = 0;
    rb->count = 0;
    return rb;
}

int omni_ring_write(OmniRingBuffer* rb, const uint8_t* data, size_t len) {
    if (!rb || !data || len == 0) return -1;
    if (rb->count + len > rb->capacity) return -2; /* full */

    for (size_t i = 0; i < len; i++) {
        rb->buffer[rb->write_pos] = data[i];
        rb->write_pos = (rb->write_pos + 1) % rb->capacity;
    }
    rb->count += len;
    return 0;
}

int omni_ring_read(OmniRingBuffer* rb, uint8_t* dest, size_t len) {
    if (!rb || !dest || len == 0) return -1;
    if (len > rb->count) return -2; /* underflow */

    for (size_t i = 0; i < len; i++) {
        dest[i] = rb->buffer[rb->read_pos];
        rb->read_pos = (rb->read_pos + 1) % rb->capacity;
    }
    rb->count -= len;
    return 0;
}

size_t omni_ring_available(const OmniRingBuffer* rb) {
    return rb ? rb->count : 0;
}

void omni_ring_destroy(OmniRingBuffer* rb) {
    if (rb) {
        omni_secure_zero(rb->buffer, rb->capacity);
        free(rb->buffer);
        free(rb);
    }
}

/* ---- Slab Allocator (fixed-size blocks) ---- */

typedef struct OmniSlab {
    uint8_t* pool;
    uint8_t* free_bitmap;
    size_t   block_size;
    size_t   num_blocks;
    size_t   used_count;
} OmniSlab;

OmniSlab* omni_slab_create(size_t block_size, size_t num_blocks) {
    if (block_size == 0 || num_blocks == 0) return NULL;
    OmniSlab* slab = (OmniSlab*)omni_sys_malloc(sizeof(OmniSlab));
    if (!slab) return NULL;
    slab->pool = (uint8_t*)omni_sys_malloc(block_size * num_blocks);
    slab->free_bitmap = (uint8_t*)omni_sys_malloc(num_blocks);
    if (!slab->pool || !slab->free_bitmap) {
        free(slab->pool); free(slab->free_bitmap); free(slab);
        return NULL;
    }
    memset(slab->free_bitmap, 1, num_blocks); /* 1 = free */
    slab->block_size = block_size;
    slab->num_blocks = num_blocks;
    slab->used_count = 0;
    return slab;
}

void* omni_slab_alloc(OmniSlab* slab) {
    if (!slab) return NULL;
    for (size_t i = 0; i < slab->num_blocks; i++) {
        if (slab->free_bitmap[i]) {
            slab->free_bitmap[i] = 0;
            slab->used_count++;
            return slab->pool + (i * slab->block_size);
        }
    }
    return NULL; /* all blocks used */
}

int omni_slab_free(OmniSlab* slab, void* ptr) {
    if (!slab || !ptr) return -1;
    size_t offset = (uint8_t*)ptr - slab->pool;
    if (offset % slab->block_size != 0) return -2;
    size_t idx = offset / slab->block_size;
    if (idx >= slab->num_blocks) return -3;
    if (slab->free_bitmap[idx]) return -4; /* double free */
    omni_secure_zero(ptr, slab->block_size);
    slab->free_bitmap[idx] = 1;
    slab->used_count--;
    return 0;
}

void omni_slab_destroy(OmniSlab* slab) {
    if (slab) {
        omni_secure_zero(slab->pool, slab->block_size * slab->num_blocks);
        free(slab->pool);
        free(slab->free_bitmap);
        free(slab);
    }
}
