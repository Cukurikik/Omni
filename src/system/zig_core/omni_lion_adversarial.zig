// Omni Lion Adversarial Distillation (Zig)
// Based on YJiangcm/Lion
// Fast system-level adversarial distillation logic.

const std = @import("std");

pub const LionError = error{
    EmptyTensors,
    DimensionMismatch,
};

pub fn compute_adversarial_loss(allocator: std.mem.Allocator, teacher: []const f32, student: []const f32) LionError!f32 {
    if (teacher.len == 0 or student.len == 0) {
        return LionError.EmptyTensors;
    }
    if (teacher.len != student.len) {
        return LionError.DimensionMismatch;
    }

    var loss: f32 = 0.0;
    for (teacher, 0..) |t_val, i| {
        const s_val = student[i];
        // Deterministic MSE computation
        const diff = t_val - s_val;
        loss += diff * diff;
    }

    return loss / @as(f32, @floatFromInt(teacher.len));
}
