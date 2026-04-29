package system

// UniGoal navigation bounds
// Odin: Embedded map tracking for spatial coordinates

import "core:mem"

MAX_MAP_CELLS :: 1_000_000 // 1 Million cell hard bound
OmniError :: enum {
    None,
    OutOfBounds,
    MemoryExhausted,
}

OmniResult :: struct(T: type) {
    value: T,
    err: OmniError,
}

GridMap :: struct {
    cells: [^]u8,
    size: u32,
}

@(export)
unigoal_init_map :: proc(size: u32) -> OmniResult(GridMap) {
    if size > MAX_MAP_CELLS {
        return OmniResult(GridMap){err = .OutOfBounds}
    }

    raw_ptr, alloc_err := mem.alloc(int(size))
    if alloc_err != nil {
        return OmniResult(GridMap){err = .MemoryExhausted}
    }

    mem.zero(raw_ptr, int(size))

    return OmniResult(GridMap){
        value = GridMap{cells = cast([^]u8)raw_ptr, size = size}, 
        err = .None
    }
}
