#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#define OMNI_MAX_ARENA_SIZE (1024 * 1024 * 64) // 64 MB hard limit

typedef struct {
    uint8_t* base;
    size_t offset;
    size_t capacity;
} ClotArena;

typedef struct {
    bool is_ok;
    ClotArena* payload;
    const char* error;
} OmniResult_Arena;

OmniResult_Arena clot_arena_create(size_t capacity) {
    OmniResult_Arena res = {0};
    
    if (capacity > OMNI_MAX_ARENA_SIZE) {
        res.is_ok = false;
        res.error = "OMNI_LIMIT: Arena size exceeds 64MB hard limit.";
        return res;
    }
    
    ClotArena* arena = (ClotArena*)malloc(sizeof(ClotArena));
    if (!arena) {
        res.is_ok = false;
        res.error = "OMNI_MEM_ERR: Failed to allocate arena struct.";
        return res;
    }
    
    arena->base = (uint8_t*)malloc(capacity);
    if (!arena->base) {
        free(arena);
        res.is_ok = false;
        res.error = "OMNI_MEM_ERR: Failed to allocate arena memory.";
        return res;
    }
    
    arena->offset = 0;
    arena->capacity = capacity;
    res.is_ok = true;
    res.payload = arena;
    
    return res;
}

void* clot_arena_alloc(ClotArena* arena, size_t size) {
    if (arena->offset + size > arena->capacity) {
        return NULL; // Monadic failure mapped at higher level
    }
    void* ptr = arena->base + arena->offset;
    arena->offset += size;
    return ptr;
}

void clot_arena_destroy(ClotArena* arena) {
    if (arena) {
        if (arena->base) {
            free(arena->base);
        }
        free(arena);
    }
}
