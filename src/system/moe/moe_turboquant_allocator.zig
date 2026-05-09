// moe_turboquant_allocator.zig — System Layer: TurboQuant Allocator
// Fast arena allocator for Apple Silicon, specialized for transient tensor buffers.

const std = @import("std");

pub const TensorArena = struct {
    buffer: []u8,
    offset: usize,

    pub fn init(allocator: std.mem.Allocator, size: usize) !TensorArena {
        const buf = try allocator.alloc(u8, size);
        return TensorArena{
            .buffer = buf,
            .offset = 0,
        };
    }

    pub fn deinit(self: *TensorArena, allocator: std.mem.Allocator) void {
        allocator.free(self.buffer);
    }

    pub fn allocate(self: *TensorArena, bytes: usize, alignment: usize) ?[]u8 {
        const aligned_offset = (self.offset + alignment - 1) & ~(alignment - 1);
        if (aligned_offset + bytes > self.buffer.len) {
            return null; // OOM in arena
        }
        
        const result = self.buffer[aligned_offset .. aligned_offset + bytes];
        self.offset = aligned_offset + bytes;
        return result;
    }

    pub fn reset(self: *TensorArena) void {
        self.offset = 0;
    }
};

test "TensorArena allocation" {
    var arena = try TensorArena.init(std.testing.allocator, 1024);
    defer arena.deinit(std.testing.allocator);
    
    const slice = arena.allocate(128, 16);
    try std.testing.expect(slice != null);
    try std.testing.expect(slice.?.len == 128);
}
