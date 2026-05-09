const std = @import("std");

/// Omni Sparse Attention (Zig)
/// System Layer
/// Implements Block-Sparse Attention (e.g. Longformer style) without undefined behavior.
/// This limits the O(N^2) complexity to O(N * W) where W is the window size.

pub fn block_sparse_attention(
    allocator: std.mem.Allocator,
    q: []const f32,
    k: []const f32,
    v: []const f32,
    seq_len: usize,
    dim: usize,
    window_size: usize,
) ![]f32 {
    var out = try allocator.alloc(f32, seq_len * dim);
    @memset(out, 0.0);

    const scale = 1.0 / @sqrt(@as(f32, @floatFromInt(dim)));

    for (0..seq_len) |i| {
        // Calculate bounds for local window
        const start_j = if (i > window_size) i - window_size else 0;
        const end_j = if (i + window_size < seq_len) i + window_size else seq_len;

        var scores = try allocator.alloc(f32, end_j - start_j);
        defer allocator.free(scores);

        var max_score: f32 = -std.math.inf(f32);

        // Q * K^T within window
        for (start_j..end_j) |j| {
            var dot: f32 = 0.0;
            for (0..dim) |d| {
                dot += q[i * dim + d] * k[j * dim + d];
            }
            dot *= scale;
            scores[j - start_j] = dot;
            if (dot > max_score) {
                max_score = dot;
            }
        }

        // Softmax
        var sum_exp: f32 = 0.0;
        for (start_j..end_j) |j| {
            scores[j - start_j] = @exp(scores[j - start_j] - max_score);
            sum_exp += scores[j - start_j];
        }

        // Output weighted sum of V
        for (0..dim) |d| {
            var acc: f32 = 0.0;
            for (start_j..end_j) |j| {
                const prob = scores[j - start_j] / sum_exp;
                acc += prob * v[j * dim + d];
            }
            out[i * dim + d] = acc;
        }
    }

    return out;
}
