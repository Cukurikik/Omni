// omni_slab.h — Slab Allocator C Header
// Layer: System / Header
//
// Exposes the Zig-based slab allocator to C and C++ components, allowing
// cross-language unified memory management for tensor buffers.

#ifndef OMNI_SLAB_H
#define OMNI_SLAB_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// Opaque handle to a Slab Allocator instance
typedef struct OmniSlabAllocator OmniSlabAllocator;

/**
 * Initialize a new slab allocator for a specific block size.
 * @param item_size The exact size in bytes of each block.
 * @return A pointer to the allocator instance.
 */
OmniSlabAllocator* omni_slab_init(size_t item_size);

/**
 * Allocate a block of memory from the slab.
 * @param slab The allocator instance.
 * @return Pointer to the allocated memory, or NULL if out of memory.
 */
void* omni_slab_alloc(OmniSlabAllocator* slab);

/**
 * Free a block of memory back to the slab.
 * @param slab The allocator instance.
 * @param ptr Pointer to the memory to free.
 */
void omni_slab_free(OmniSlabAllocator* slab, void* ptr);

/**
 * Destroy the slab allocator and free all backing pages.
 * @param slab The allocator instance.
 */
void omni_slab_deinit(OmniSlabAllocator* slab);

#ifdef __cplusplus
}
#endif

#endif // OMNI_SLAB_H
