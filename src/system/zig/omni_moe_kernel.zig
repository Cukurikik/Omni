const std = @import("std");

// OMNI MOTHER: Zig MoE Kernel
// Fast execution of routing logic

export fn omni_zig_route_top1(logits: [*]f32, num_experts: usize) usize {
    var max_val: f32 = -std.math.inf(f32);
    var best_idx: usize = 0;
    
    var i: usize = 0;
    while (i < num_experts) : (i += 1) {
        if (logits[i] > max_val) {
            max_val = logits[i];
            best_idx = i;
        }
    }
    return best_idx;
}
