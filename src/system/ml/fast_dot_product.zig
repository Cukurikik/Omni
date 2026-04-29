const std = @import("std");

pub fn dot_product(a: []const f32, b: []const f32) !f32 {
    if (a.len != b.len) {
        return error.DimensionMismatch;
    }
    
    var sum: f32 = 0.0;
    for (a, 0..) |_, i| {
        sum += a[i] * b[i];
    }
    return sum;
}
