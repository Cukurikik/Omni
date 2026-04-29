/* Omni KG-LLM Arena Allocator (C)
 * System Layer: Custom arena for batched KG triple storage.
 * Ref: yao8839836/kg-llm */

#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define ARENA_BLOCK_SIZE (1024 * 1024)

typedef struct {
    uint8_t *base;
    size_t offset;
    size_t capacity;
} OmniKGArena;

int omni_kg_arena_init(OmniKGArena *arena, size_t cap) {
    if (!arena || cap == 0) return -1;
    arena->base = (uint8_t *)malloc(cap);
    if (!arena->base) return -1;
    arena->offset = 0;
    arena->capacity = cap;
    return 0;
}

void *omni_kg_arena_alloc(OmniKGArena *arena, size_t size) {
    if (!arena || arena->offset + size > arena->capacity) return NULL;
    void *ptr = arena->base + arena->offset;
    arena->offset += size;
    return ptr;
}

void omni_kg_arena_reset(OmniKGArena *arena) {
    if (arena) arena->offset = 0;
}

void omni_kg_arena_free(OmniKGArena *arena) {
    if (arena && arena->base) { free(arena->base); arena->base = NULL; }
}
