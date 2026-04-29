#include <stdlib.h>
#include <stdint.h>
#include <stddef.h>

typedef struct Arena {
    uint8_t *buffer;
    size_t length;
    size_t offset;
} Arena;

Arena* omni_arena_create(size_t length) {
    Arena *arena = (Arena*)malloc(sizeof(Arena));
    if (!arena) return NULL;
    arena->buffer = (uint8_t*)malloc(length);
    if (!arena->buffer) {
        free(arena);
        return NULL;
    }
    arena->length = length;
    arena->offset = 0;
    return arena;
}

void* omni_arena_alloc(Arena *arena, size_t size, size_t alignment) {
    size_t current = (size_t)(arena->buffer + arena->offset);
    size_t offset = (alignment - (current % alignment)) % alignment;
    if (arena->offset + offset + size > arena->length) {
        return NULL; // Out of memory
    }
    arena->offset += offset;
    void *ptr = arena->buffer + arena->offset;
    arena->offset += size;
    return ptr;
}

void omni_arena_free_all(Arena *arena) {
    arena->offset = 0;
}

void omni_arena_destroy(Arena *arena) {
    if (arena) {
        if (arena->buffer) free(arena->buffer);
        free(arena);
    }
}
