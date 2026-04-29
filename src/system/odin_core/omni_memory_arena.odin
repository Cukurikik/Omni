package omni_system

import "core:mem"

// Omni Memory Arena in Odin
// Zero-mock, deterministic memory management for System Layer

OmniArenaError :: enum {
    None,
    OutOfMemory,
    InvalidAlignment,
}

OmniArena :: struct {
    backing: []u8,
    offset:  int,
}

init_arena :: proc(arena: ^OmniArena, size: int) -> OmniArenaError {
    if size <= 0 {
        return .InvalidAlignment
    }
    
    // Deterministic allocation via Odin core mem
    backing_mem, err := mem.alloc_bytes(size)
    if err != nil {
        return .OutOfMemory
    }
    
    arena.backing = backing_mem
    arena.offset = 0
    return .None
}
