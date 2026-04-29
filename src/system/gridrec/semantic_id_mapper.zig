const std = @import("std");

pub fn OmniResult(comptime T: type) type {
    return struct {
        value: T,
        error_msg: ?[]const u8,
        is_ok: bool,
    };
}

pub fn map_semantic_id(user_vector: [*]f32, item_vectors: [*]f32, num_items: usize, dim: usize) OmniResult(usize) {
    if (num_items == 0 or dim == 0) return .{ .value = 0, .error_msg = "Invalid dimensions", .is_ok = false };
    
    var best_idx: usize = 0;
    var max_sim: f32 = -1.0;
    
    // Zig memory-safe native dot product for GRID Semantic IDs
    var i: usize = 0;
    while (i < num_items) : (i += 1) {
        var sim: f32 = 0.0;
        var j: usize = 0;
        while (j < dim) : (j += 1) {
            sim += user_vector[j] * item_vectors[i * dim + j];
        }
        if (sim > max_sim) {
            max_sim = sim;
            best_idx = i;
        }
    }
    
    return .{ .value = best_idx, .error_msg = null, .is_ok = true };
}
