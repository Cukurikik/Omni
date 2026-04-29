const std = @import("std");

pub const MatrixError = error{
    DimensionMismatch,
};

pub fn matrix_multiply(allocator: std.mem.Allocator, A: [][]const f32, B: [][]const f32) ![][]f32 {
    const m = A.len;
    if (m == 0) return MatrixError.DimensionMismatch;
    const n = A[0].len;
    if (B.len != n) return MatrixError.DimensionMismatch;
    const p = B[0].len;

    var C = try allocator.alloc([]f32, m);
    for (C, 0..) |*row, i| {
        row.* = try allocator.alloc(f32, p);
        for (row.*, 0..) |*val, j| {
            var sum: f32 = 0.0;
            for (0..n) |k| {
                sum += A[i][k] * B[k][j];
            }
            val.* = sum;
        }
    }
    return C;
}
