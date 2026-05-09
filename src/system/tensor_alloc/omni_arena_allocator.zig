// @omni-layer System | @omni-lang Zig | @omni-batch 17
// @omni-description Arena allocator for zero-copy tensor operations with
// comptime-verified alignment and deterministic deallocation.
const std = @import("std");

pub const ArenaError = error{OutOfMemory, InvalidAlignment, DoubleFree};

pub const TensorArena = struct {
    buffer: []u8,
    offset: usize,
    capacity: usize,
    allocations: usize,
    peak_usage: usize,

    pub fn init(buffer: []u8) TensorArena {
        return .{
            .buffer = buffer,
            .offset = 0,
            .capacity = buffer.len,
            .allocations = 0,
            .peak_usage = 0,
        };
    }

    pub fn alloc(self: *TensorArena, comptime T: type, count: usize) ArenaError![]T {
        const alignment = @alignOf(T);
        const aligned_offset = (self.offset + alignment - 1) & ~(alignment - 1);
        const byte_count = count * @sizeOf(T);

        if (aligned_offset + byte_count > self.capacity) {
            return ArenaError.OutOfMemory;
        }

        const ptr = @as([*]T, @ptrCast(@alignCast(self.buffer[aligned_offset..].ptr)));
        self.offset = aligned_offset + byte_count;
        self.allocations += 1;
        if (self.offset > self.peak_usage) {
            self.peak_usage = self.offset;
        }
        return ptr[0..count];
    }

    pub fn allocFloat32(self: *TensorArena, count: usize) ArenaError![]f32 {
        return self.alloc(f32, count);
    }

    pub fn allocFloat64(self: *TensorArena, count: usize) ArenaError![]f64 {
        return self.alloc(f64, count);
    }

    pub fn allocInt32(self: *TensorArena, count: usize) ArenaError![]i32 {
        return self.alloc(i32, count);
    }

    pub fn reset(self: *TensorArena) void {
        self.offset = 0;
        self.allocations = 0;
    }

    pub fn usedBytes(self: *const TensorArena) usize {
        return self.offset;
    }

    pub fn remainingBytes(self: *const TensorArena) usize {
        return self.capacity - self.offset;
    }

    pub fn utilizationPercent(self: *const TensorArena) f64 {
        if (self.capacity == 0) return 0.0;
        return @as(f64, @floatFromInt(self.offset)) / @as(f64, @floatFromInt(self.capacity)) * 100.0;
    }
};

pub fn dot_product_f32(a: []const f32, b: []const f32) f32 {
    const n = @min(a.len, b.len);
    var sum: f32 = 0.0;
    var i: usize = 0;
    while (i < n) : (i += 1) {
        sum += a[i] * b[i];
    }
    return sum;
}

pub fn vector_norm_f32(v: []const f32) f32 {
    return @sqrt(dot_product_f32(v, v));
}

pub fn softmax_inplace(logits: []f32) void {
    var max_val: f32 = logits[0];
    for (logits[1..]) |val| {
        if (val > max_val) max_val = val;
    }
    var sum: f32 = 0.0;
    for (logits) |*val| {
        val.* = @exp(val.* - max_val);
        sum += val.*;
    }
    for (logits) |*val| {
        val.* /= (sum + 1e-8);
    }
}
