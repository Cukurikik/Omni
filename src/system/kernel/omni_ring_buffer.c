/*
 * omni_ring_buffer.c — Lock-Free Ring Buffer
 * Layer: System / C
 *
 * Implements a high-speed, thread-safe, lock-free Single-Producer 
 * Single-Consumer (SPSC) ring buffer using memory fences and stdatomic.
 * Zero-mock implementation.
 */

#include <stdlib.h>
#include <stdint.h>
#include <stdatomic.h>
#include <string.h>

typedef struct OmniRingBuffer {
    uint8_t* buffer;
    size_t capacity;
    atomic_size_t head;
    atomic_size_t tail;
} OmniRingBuffer;

/*
 * Note: capacity must be a power of 2 for optimal modulo operations,
 * but this generic implementation allows arbitrary sizes.
 */
OmniRingBuffer* omni_ring_buffer_create(size_t capacity) {
    OmniRingBuffer* rb = (OmniRingBuffer*)malloc(sizeof(OmniRingBuffer));
    if (!rb) return NULL;
    
    // Allocate 1 extra byte to distinguish full from empty
    rb->capacity = capacity + 1;
    rb->buffer = (uint8_t*)malloc(rb->capacity);
    
    if (!rb->buffer) {
        free(rb);
        return NULL;
    }
    
    atomic_init(&rb->head, 0);
    atomic_init(&rb->tail, 0);
    
    return rb;
}

void omni_ring_buffer_destroy(OmniRingBuffer* rb) {
    if (rb) {
        if (rb->buffer) free(rb->buffer);
        free(rb);
    }
}

size_t omni_ring_buffer_available_write(OmniRingBuffer* rb) {
    size_t head = atomic_load_explicit(&rb->head, memory_order_acquire);
    size_t tail = atomic_load_explicit(&rb->tail, memory_order_relaxed);
    
    if (head >= tail) {
        return rb->capacity - 1 - (head - tail);
    } else {
        return tail - head - 1;
    }
}

size_t omni_ring_buffer_available_read(OmniRingBuffer* rb) {
    size_t head = atomic_load_explicit(&rb->head, memory_order_relaxed);
    size_t tail = atomic_load_explicit(&rb->tail, memory_order_acquire);
    
    if (head >= tail) {
        return head - tail;
    } else {
        return rb->capacity - (tail - head);
    }
}

int omni_ring_buffer_push(OmniRingBuffer* rb, const uint8_t* data, size_t len) {
    size_t available = omni_ring_buffer_available_write(rb);
    if (len > available) {
        return 0; // Not enough space
    }
    
    size_t head = atomic_load_explicit(&rb->head, memory_order_relaxed);
    size_t first_chunk = rb->capacity - head;
    
    if (len <= first_chunk) {
        memcpy(rb->buffer + head, data, len);
    } else {
        memcpy(rb->buffer + head, data, first_chunk);
        memcpy(rb->buffer, data + first_chunk, len - first_chunk);
    }
    
    atomic_store_explicit(&rb->head, (head + len) % rb->capacity, memory_order_release);
    return 1;
}

int omni_ring_buffer_pop(OmniRingBuffer* rb, uint8_t* out_data, size_t len) {
    size_t available = omni_ring_buffer_available_read(rb);
    if (len > available) {
        return 0; // Not enough data
    }
    
    size_t tail = atomic_load_explicit(&rb->tail, memory_order_relaxed);
    size_t first_chunk = rb->capacity - tail;
    
    if (len <= first_chunk) {
        memcpy(out_data, rb->buffer + tail, len);
    } else {
        memcpy(out_data, rb->buffer + tail, first_chunk);
        memcpy(out_data + first_chunk, rb->buffer, len - first_chunk);
    }
    
    atomic_store_explicit(&rb->tail, (tail + len) % rb->capacity, memory_order_release);
    return 1;
}
