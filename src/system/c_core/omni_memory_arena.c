// OMNI System Layer: High-Performance Arena Allocator in C
#include <stdlib.h>
#include <stdint.h>

typedef struct {
    uint8_t* buffer;
    size_t size;
    size_t offset;
} OmniArena;

OmniArena* omni_arena_create(size_t size) {
    OmniArena* arena = (OmniArena*)malloc(sizeof(OmniArena));
    arena->buffer = (uint8_t*)malloc(size);
    arena->size = size;
    arena->offset = 0;
    return arena;
}

void* omni_arena_alloc(OmniArena* arena, size_t size) {
    if (arena->offset + size > arena->size) return NULL;
    void* ptr = arena->buffer + arena->offset;
    arena->offset += size;
    return ptr;
}

void omni_arena_free(OmniArena* arena) {
    free(arena->buffer);
    free(arena);
}
