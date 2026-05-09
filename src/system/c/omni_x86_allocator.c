#include <stddef.h>
#include <stdint.h>
#include <sys/mman.h>

#define OMNI_ARENA_SIZE 1024 * 1024 * 64 // 64 MB

typedef struct {
    uint8_t* base;
    size_t offset;
    size_t capacity;
} OmniX86Arena;

OmniX86Arena omni_init_arena() {
    uint8_t* mem = mmap(NULL, OMNI_ARENA_SIZE, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    OmniX86Arena arena = { .base = mem, .offset = 0, .capacity = OMNI_ARENA_SIZE };
    return arena;
}

void* omni_arena_alloc(OmniX86Arena* arena, size_t size, size_t align) {
    size_t current_ptr = (size_t)(arena->base + arena->offset);
    size_t aligned_ptr = (current_ptr + align - 1) & ~(align - 1);
    size_t shift = aligned_ptr - current_ptr;
    
    if (arena->offset + shift + size > arena->capacity) {
        return NULL; // Out of memory
    }
    
    arena->offset += shift + size;
    return (void*)aligned_ptr;
}

void omni_arena_free_all(OmniX86Arena* arena) {
    arena->offset = 0;
}
