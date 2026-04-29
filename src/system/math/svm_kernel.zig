const std = @import("std");
const math = std.math;

pub fn rbf_kernel(x1: []const f64, x2: []const f64, gamma: f64) f64 {
    var sum_sq_diff: f64 = 0.0;
    for (x1, 0..) |val1, i| {
        const diff = val1 - x2[i];
        sum_sq_diff += diff * diff;
    }
    return math.exp(-gamma * sum_sq_diff);
}

pub fn linear_kernel(x1: []const f64, x2: []const f64) f64 {
    var dot: f64 = 0.0;
    for (x1, 0..) |val, i| {
        dot += val * x2[i];
    }
    return dot;
}
