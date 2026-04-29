package llmrank

// LLMRank Zero-Shot Ranking Score Compute Matrix
// Native memory alignment for high-performance ranking inference

import "core:fmt"
import "core:mem"

MAX_ITEMS_TO_RANK :: 100_000
OmniError :: enum {
    None,
    ItemCountExceeded,
    MemoryExhausted,
}

OmniResult :: struct(T: type) {
    value: T,
    err: OmniError,
}

RankMatrix :: struct {
    scores: [^]f32,
    count: u32,
}

@(export)
llmrank_allocate_matrix :: proc(num_items: u32) -> OmniResult(RankMatrix) {
    if num_items > MAX_ITEMS_TO_RANK {
        return OmniResult(RankMatrix){err = .ItemCountExceeded}
    }

    bytes_required := int(num_items) * size_of(f32)
    raw_ptr, alloc_err := mem.alloc(bytes_required)
    
    if alloc_err != nil {
        return OmniResult(RankMatrix){err = .MemoryExhausted}
    }

    mem.zero(raw_ptr, bytes_required)

    matrix := RankMatrix{
        scores = cast([^]f32)raw_ptr,
        count = num_items,
    }

    return OmniResult(RankMatrix){value = matrix, err = .None}
}
