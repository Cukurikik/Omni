const std = @import("std");

pub const DmaEngine = struct {
    ring_buffer: []u8,
    head: usize,
    tail: usize,

    pub fn init(allocator: std.mem.Allocator, size: usize) !DmaEngine {
        return DmaEngine{
            .ring_buffer = try allocator.alloc(u8, size),
            .head = 0,
            .tail = 0,
        };
    }

    pub fn push(self: *DmaEngine, data: []const u8) bool {
        const space = self.ring_buffer.len - self.head;
        if (space < data.len) return false;
        std.mem.copy(u8, self.ring_buffer[self.head..], data);
        self.head += data.len;
        return true;
    }
};
