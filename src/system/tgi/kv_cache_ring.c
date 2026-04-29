#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

// OMNI TGI: KV Cache Ring Buffer
// High-performance C ring buffer for managing continuous batching request queues in Text-Generation-Inference.
// Source: huggingface/text-generation-inference

typedef enum {
    RING_SUCCESS = 0,
    RING_ERR_FULL = 1,
    RING_ERR_EMPTY = 2,
    RING_ERR_NULL = 3
} RingError;

typedef struct {
    int request_id;
    int prompt_tokens;
    int max_new_tokens;
} TGIRequest;

typedef struct {
    TGIRequest* buffer;
    size_t capacity;
    size_t head;
    size_t tail;
    size_t count;
} RequestRingBuffer;

// Initialize the ring buffer
RingError tgi_ring_init(RequestRingBuffer* ring, size_t capacity) {
    if (!ring || capacity == 0) return RING_ERR_NULL;
    
    ring->buffer = (TGIRequest*)malloc(capacity * sizeof(TGIRequest));
    if (!ring->buffer) return RING_ERR_NULL;
    
    ring->capacity = capacity;
    ring->head = 0;
    ring->tail = 0;
    ring->count = 0;
    
    return RING_SUCCESS;
}

// Push a new request onto the ring (enqueue)
RingError tgi_ring_push(RequestRingBuffer* ring, TGIRequest req) {
    if (!ring || !ring->buffer) return RING_ERR_NULL;
    if (ring->count >= ring->capacity) return RING_ERR_FULL;
    
    ring->buffer[ring->tail] = req;
    ring->tail = (ring->tail + 1) % ring->capacity;
    ring->count++;
    
    return RING_SUCCESS;
}

// Pop an existing request from the ring (dequeue)
RingError tgi_ring_pop(RequestRingBuffer* ring, TGIRequest* out_req) {
    if (!ring || !ring->buffer || !out_req) return RING_ERR_NULL;
    if (ring->count == 0) return RING_ERR_EMPTY;
    
    *out_req = ring->buffer[ring->head];
    ring->head = (ring->head + 1) % ring->capacity;
    ring->count--;
    
    return RING_SUCCESS;
}

// Cleanup
void tgi_ring_free(RequestRingBuffer* ring) {
    if (ring && ring->buffer) {
        free(ring->buffer);
        ring->buffer = NULL;
        ring->capacity = 0;
        ring->count = 0;
    }
}
