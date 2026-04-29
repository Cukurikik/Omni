// Omni DeepSpeed Allocator (C)
// System Layer: Bare-metal memory block manager for distributed tensor training.

#include <stddef.h>
#include <stdint.h>

#define OMNI_MEM_SUCCESS 0
#define OMNI_MEM_ERR_OOM 1
#define OMNI_MEM_ERR_INVALID 2

typedef struct {
    uint8_t* base_ptr;
    size_t capacity;
    size_t offset;
} OmniArena;

int omni_deepspeed_allocate(OmniArena* arena, size_t alloc_size, void** out_ptr) {
    if (!arena || !arena->base_ptr || !out_ptr) {
        return OMNI_MEM_ERR_INVALID;
    }
    
    // Ensure 16-byte alignment for Tensor Cores
    size_t aligned_size = (alloc_size + 15) & ~15;

    if (arena->offset + aligned_size > arena->capacity) {
        *out_ptr = NULL;
        return OMNI_MEM_ERR_OOM;
    }

    *out_ptr = arena->base_ptr + arena->offset;
    arena->offset += aligned_size;

    return OMNI_MEM_SUCCESS;
}
