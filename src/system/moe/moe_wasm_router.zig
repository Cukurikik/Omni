// moe_wasm_router.zig — WASM-Target MoE Router
// Layer: System / WASM — MoE Edge Inference
//
// Minimal MoE router compiled to WebAssembly for edge/browser
// inference. Implements softmax and top-k in pure Zig without
// stdlib dependencies for minimal WASM binary size.

const std = @import("std");

pub const MAX_EXPERTS: usize = 256;
pub const MAX_TOP_K: usize = 16;

pub const RouterResult = struct {
    expert_ids: [MAX_TOP_K]u16,
    weights: [MAX_TOP_K]f32,
    num_selected: u8,
};

/// Compute softmax in-place over a slice of f32.
pub fn softmax(logits: []f32) void {
    if (logits.len == 0) return;

    // Find max for numerical stability
    var max_val: f32 = logits[0];
    for (logits[1..]) |v| {
        if (v > max_val) max_val = v;
    }

    // Compute exp and sum
    var sum: f32 = 0.0;
    for (logits) |*v| {
        v.* = @exp(v.* - max_val);
        sum += v.*;
    }

    // Normalize
    if (sum > 0.0) {
        const inv = 1.0 / sum;
        for (logits) |*v| {
            v.* *= inv;
        }
    }
}

/// Select top-k experts from probability distribution.
pub fn topk(probs: []const f32, k: u8) RouterResult {
    var result = RouterResult{
        .expert_ids = [_]u16{0} ** MAX_TOP_K,
        .weights = [_]f32{0.0} ** MAX_TOP_K,
        .num_selected = 0,
    };

    const actual_k: u8 = if (k > @as(u8, @intCast(probs.len))) @intCast(probs.len) else k;

    // Selection sort for small k
    var used = [_]bool{false} ** MAX_EXPERTS;

    for (0..actual_k) |ki| {
        var best_idx: usize = 0;
        var best_val: f32 = -1.0;
        for (probs, 0..) |p, j| {
            if (!used[j] and p > best_val) {
                best_val = p;
                best_idx = j;
            }
        }
        result.expert_ids[ki] = @intCast(best_idx);
        result.weights[ki] = best_val;
        used[best_idx] = true;
    }

    result.num_selected = actual_k;

    // Normalize weights
    var wsum: f32 = 0.0;
    for (0..actual_k) |ki| {
        wsum += result.weights[ki];
    }
    if (wsum > 0.0) {
        const inv = 1.0 / wsum;
        for (0..actual_k) |ki| {
            result.weights[ki] *= inv;
        }
    }

    return result;
}

/// Full routing pipeline for a single token.
pub fn route_token(logits: []f32, k: u8, temperature: f32) RouterResult {
    // Apply temperature
    if (temperature > 0.0 and temperature != 1.0) {
        const inv_t = 1.0 / temperature;
        for (logits) |*v| {
            v.* *= inv_t;
        }
    }

    softmax(logits);
    return topk(logits, k);
}

/// Batch routing: route multiple tokens.
pub fn route_batch(
    all_logits: []f32,
    num_tokens: u32,
    num_experts: u16,
    k: u8,
    temperature: f32,
    results: []RouterResult,
) void {
    for (0..num_tokens) |t| {
        const start = t * @as(usize, num_experts);
        const end = start + @as(usize, num_experts);
        var token_logits = all_logits[start..end];
        results[t] = route_token(token_logits, k, temperature);
    }
}

/// Compute load balance loss from routing results.
pub fn compute_lb_loss(
    results: []const RouterResult,
    num_tokens: u32,
    num_experts: u16,
) f32 {
    var counts = [_]u32{0} ** MAX_EXPERTS;
    const ne: usize = @intCast(num_experts);

    for (results[0..num_tokens]) |r| {
        if (r.num_selected > 0) {
            counts[@as(usize, r.expert_ids[0])] += 1;
        }
    }

    const inv_n: f32 = 1.0 / @as(f32, @floatFromInt(if (num_tokens > 0) num_tokens else 1));
    var loss: f32 = 0.0;
    for (0..ne) |e| {
        const f: f32 = @as(f32, @floatFromInt(counts[e])) * inv_n;
        loss += f * f; // simplified: f^2 instead of f*p
    }
    return loss * @as(f32, @floatFromInt(num_experts));
}

// WASM exports
export fn wasm_softmax(ptr: [*]f32, len: u32) void {
    softmax(ptr[0..len]);
}

export fn wasm_route_token(ptr: [*]f32, len: u32, k: u8, temp: f32) RouterResult {
    return route_token(ptr[0..len], k, temp);
}

test "softmax normalization" {
    var logits = [_]f32{ 1.0, 2.0, 3.0, 4.0 };
    softmax(&logits);
    var sum: f32 = 0.0;
    for (logits) |v| sum += v;
    try std.testing.expect(@abs(sum - 1.0) < 0.001);
}

test "topk selection" {
    const probs = [_]f32{ 0.1, 0.3, 0.05, 0.4, 0.15 };
    const result = topk(&probs, 2);
    try std.testing.expectEqual(@as(u8, 2), result.num_selected);
    try std.testing.expectEqual(@as(u16, 3), result.expert_ids[0]); // highest prob
    try std.testing.expectEqual(@as(u16, 1), result.expert_ids[1]); // second highest
}
