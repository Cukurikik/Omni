package deita

import "core:fmt"

OmniResult :: struct(T: typeid) {
    value: T,
    error: string,
    is_ok: bool,
}

evaluate_instruction :: proc(score: f32) -> OmniResult(bool) {
    if score < 0.0 || score > 1.0 {
        return OmniResult(bool){false, "Score out of bounds", false}
    }
    
    // Odin low-level, zero-allocation logic for Deita
    is_good := score > 0.8
    return OmniResult(bool){is_good, "", true}
}
