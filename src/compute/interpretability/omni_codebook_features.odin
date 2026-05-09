package omni_codebook

import "core:fmt"
import "core:math"
import "core:mem"

// Codebook Features: Sparse and discrete interpretability tool for neural networks
// Maps continuous activation vectors into a sparse dictionary of interpretable codebook vectors.

Codebook :: struct {
    num_codes: int,
    dim: int,
    codes: []f32, // Flattened 2D array [num_codes][dim]
}

init_codebook :: proc(num_codes: int, dim: int) -> Codebook {
    codes := make([]f32, num_codes * dim)
    // Initialize with small random values
    for i in 0..<num_codes * dim {
        codes[i] = 0.01 // Simplified init
    }
    return Codebook{num_codes, dim, codes}
}

destroy_codebook :: proc(cb: ^Codebook) {
    delete(cb.codes)
}

// Find the nearest codebook vector for a given activation vector (L2 Distance)
quantize_activation :: proc(cb: ^Codebook, activation: []f32) -> (int, f32) {
    if len(activation) != cb.dim {
        return -1, -1.0
    }

    best_idx := -1
    min_dist := math.F32_MAX

    for i in 0..<cb.num_codes {
        dist: f32 = 0.0
        base := i * cb.dim
        for j in 0..<cb.dim {
            diff := activation[j] - cb.codes[base + j]
            dist += diff * diff
        }
        
        if dist < min_dist {
            min_dist = dist
            best_idx = i
        }
    }

    return best_idx, min_dist
}

update_codebook_ema :: proc(cb: ^Codebook, activation: []f32, best_idx: int, decay: f32) {
    base := best_idx * cb.dim
    for j in 0..<cb.dim {
        // Exponential Moving Average update
        cb.codes[base + j] = cb.codes[base + j] * decay + activation[j] * (1.0 - decay)
    }
}
