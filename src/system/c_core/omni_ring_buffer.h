// OMNI System — C Lock-Free SPSC Ring Buffer for Streaming
#ifndef OMNI_RING_BUFFER_H
#define OMNI_RING_BUFFER_H
#include <stdint.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    uint8_t* buffer; uint32_t capacity; uint32_t mask;
    _Atomic uint32_t write_pos; _Atomic uint32_t read_pos;
    _Atomic uint64_t total_written; _Atomic uint64_t total_read;
} omni_ring_t;

static inline omni_ring_t* omni_ring_create(uint32_t cap) {
    cap |= cap>>1; cap |= cap>>2; cap |= cap>>4; cap |= cap>>8; cap |= cap>>16; cap++;
    omni_ring_t* r = calloc(1, sizeof(omni_ring_t));
    r->buffer = malloc(cap); r->capacity = cap; r->mask = cap-1;
    return r;
}
static inline void omni_ring_destroy(omni_ring_t* r) { free(r->buffer); free(r); }
static inline uint32_t omni_ring_avail(const omni_ring_t* r) {
    return atomic_load(&r->write_pos) - atomic_load(&r->read_pos);
}
static inline bool omni_ring_write(omni_ring_t* r, const uint8_t* d, uint32_t n) {
    if (r->capacity - omni_ring_avail(r) < n) return false;
    uint32_t w = atomic_load(&r->write_pos), p = w & r->mask, f = r->capacity - p;
    if (f >= n) memcpy(r->buffer+p, d, n);
    else { memcpy(r->buffer+p, d, f); memcpy(r->buffer, d+f, n-f); }
    atomic_store(&r->write_pos, w+n); atomic_fetch_add(&r->total_written, n);
    return true;
}
static inline uint32_t omni_ring_read(omni_ring_t* r, uint8_t* d, uint32_t n) {
    uint32_t a = omni_ring_avail(r); if (a < n) n = a; if (!n) return 0;
    uint32_t rd = atomic_load(&r->read_pos), p = rd & r->mask, f = r->capacity - p;
    if (f >= n) memcpy(d, r->buffer+p, n);
    else { memcpy(d, r->buffer+p, f); memcpy(d+f, r->buffer, n-f); }
    atomic_store(&r->read_pos, rd+n); atomic_fetch_add(&r->total_read, n);
    return n;
}
#endif
