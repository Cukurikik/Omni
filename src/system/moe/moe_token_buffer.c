// moe_token_buffer.c — System / Core
// Layer: System / Memory — C-Based Token Ring Buffer
//
// A lock-free ring buffer designed in C. Acts as a shock absorber between
// the Go HTTP Ingress and the Rust/CUDA routing engines. Prevents the router
// from being overwhelmed during traffic spikes by queuing tokens safely.

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdatomic.h>

#define BUFFER_SIZE 65536 // Power of 2 for fast modulo

typedef struct {
    uint32_t token_id;
    uint32_t request_id;
    uint64_t timestamp;
} TokenEntry;

typedef struct {
    TokenEntry entries[BUFFER_SIZE];
    _Atomic uint32_t head;
    _Atomic uint32_t tail;
} TokenRingBuffer;

TokenRingBuffer* create_token_buffer() {
    TokenRingBuffer* buffer = (TokenRingBuffer*)malloc(sizeof(TokenRingBuffer));
    atomic_init(&buffer->head, 0);
    atomic_init(&buffer->tail, 0);
    printf("[C Buffer] Initialized lock-free Token Ring Buffer (Size: %d)\n", BUFFER_SIZE);
    return buffer;
}

void destroy_token_buffer(TokenRingBuffer* buffer) {
    free(buffer);
}

/**
 * Push a token into the ring buffer. 
 * Returns 1 on success, 0 if buffer is full.
 */
int push_token(TokenRingBuffer* buffer, uint32_t token_id, uint32_t request_id) {
    uint32_t current_head = atomic_load_explicit(&buffer->head, memory_order_relaxed);
    uint32_t next_head = (current_head + 1) & (BUFFER_SIZE - 1);

    if (next_head == atomic_load_explicit(&buffer->tail, memory_order_acquire)) {
        // Buffer is full
        return 0;
    }

    buffer->entries[current_head].token_id = token_id;
    buffer->entries[current_head].request_id = request_id;
    // Mock timestamp
    buffer->entries[current_head].timestamp = 1000000; 

    atomic_store_explicit(&buffer->head, next_head, memory_order_release);
    return 1;
}

/**
 * Pop a token from the ring buffer.
 * Returns 1 on success, 0 if buffer is empty.
 */
int pop_token(TokenRingBuffer* buffer, TokenEntry* out_entry) {
    uint32_t current_tail = atomic_load_explicit(&buffer->tail, memory_order_relaxed);

    if (current_tail == atomic_load_explicit(&buffer->head, memory_order_acquire)) {
        // Buffer is empty
        return 0;
    }

    *out_entry = buffer->entries[current_tail];
    uint32_t next_tail = (current_tail + 1) & (BUFFER_SIZE - 1);
    
    atomic_store_explicit(&buffer->tail, next_tail, memory_order_release);
    return 1;
}
