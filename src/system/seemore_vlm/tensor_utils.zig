const std = @import("std");

pub fn create_tensor_buffer(allocator: std.mem.Allocator, size: usize) ![]f32 {
    if (size == 0) return error.InvalidSize;
    return allocator.alloc(f32, size);
}
