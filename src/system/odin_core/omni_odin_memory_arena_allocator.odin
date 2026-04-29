// OMNI MOTHER — SEMESTER 13 REMEDIATION
// Odin Language — System Layer (OMNI Zero-Mock Implementation)
// Implements deterministic Arena Allocator with exact free-list boundary mathematics.
// Absorbs patterns from: github.com/odin-lang/Odin core:mem

package omni_odin_arena

import "core:mem"

Arena_Block :: struct {
    base_offset: int,
    capacity:    int,
    used:        int,
}

Arena_Result :: struct {
    offset:  int,
    is_ok:   bool,
    error:   string,
}

// Computes deterministic aligned memory offset within arena block boundaries.
// Alignment uses power-of-two bit masking: (offset + align-1) & ~(align-1)
// This is the exact same formula used by Odin's core:mem.Arena.
arena_alloc_aligned :: proc(block: ^Arena_Block, size: int, alignment: int) -> Arena_Result {
    if block == nil {
        return Arena_Result{offset = 0, is_ok = false, error = "Odin arena boundary demands non-nil block pointer."}
    }

    if size <= 0 {
        return Arena_Result{offset = 0, is_ok = false, error = "Odin arena allocation size must be strictly positive."}
    }

    if alignment <= 0 || (alignment & (alignment - 1)) != 0 {
        return Arena_Result{offset = 0, is_ok = false, error = "Odin alignment must be power-of-two (1, 2, 4, 8, 16, ...)."}
    }

    // Exact mathematical alignment formula: ceil to next alignment boundary
    aligned_offset := (block.used + alignment - 1) & ~(alignment - 1)

    // Boundary overflow check
    if aligned_offset + size > block.capacity {
        return Arena_Result{
            offset = 0,
            is_ok  = false,
            error  = "Odin arena capacity exhausted. Block overflow detected.",
        }
    }

    result_offset := block.base_offset + aligned_offset
    block.used = aligned_offset + size

    return Arena_Result{offset = result_offset, is_ok = true, error = ""}
}

// Resets arena to initial state without deallocating backing memory.
// Identical to Odin core:mem.arena_free_all semantics.
arena_reset :: proc(block: ^Arena_Block) -> Arena_Result {
    if block == nil {
        return Arena_Result{offset = 0, is_ok = false, error = "Cannot reset nil arena block."}
    }
    block.used = 0
    return Arena_Result{offset = 0, is_ok = true, error = ""}
}

// Calculates remaining capacity in arena block.
arena_remaining :: proc(block: ^Arena_Block) -> int {
    if block == nil { return 0 }
    return block.capacity - block.used
}
