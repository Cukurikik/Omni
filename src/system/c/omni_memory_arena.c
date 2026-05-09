// OMNI System — Memory Arena
// Extremely fast memory allocation for inference C extensions

#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>

typedef struct {
    uint8_t* buffer;
    size_t capacity;
    size_t offset;
} OmniArena;

OmniArena* omni_arena_create(size_t capacity_bytes) {
    OmniArena* arena = (OmniArena*)malloc(sizeof(OmniArena));
    if (!arena) return NULL;
    
    arena->buffer = (uint8_t*)malloc(capacity_bytes);
    if (!arena->buffer) {
        free(arena);
        return NULL;
    }
    
    arena->capacity = capacity_bytes;
    arena->offset = 0;
    return arena;
}

void* omni_arena_alloc(OmniArena* arena, size_t size) {
    // Ensure 8-byte alignment
    size_t aligned_size = (size + 7) & ~7;
    
    if (arena->offset + aligned_size > arena->capacity) {
        return NULL; // Out of memory
    }
    
    void* ptr = arena->buffer + arena->offset;
    arena->offset += aligned_size;
    return ptr;
}

void omni_arena_reset(OmniArena* arena) {
    arena->offset = 0;
}

void omni_arena_destroy(OmniArena* arena) {
    if (arena) {
        free(arena->buffer);
        free(arena);
    }
}
