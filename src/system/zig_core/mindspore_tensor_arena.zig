const std = @import("std");

pub const MindsporeTensorArena = struct {
    allocator: std.mem.Allocator,
    memory: []u8,

    pub fn init(allocator: std.mem.Allocator, size: usize) !MindsporeTensorArena {
        const mem = try allocator.alloc(u8, size);
        return MindsporeTensorArena{
            .allocator = allocator,
            .memory = mem,
        };
    }

    pub fn deinit(self: *MindsporeTensorArena) void {
        self.allocator.free(self.memory);
    }
};
