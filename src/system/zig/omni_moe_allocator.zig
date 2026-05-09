const std = @import("std");

// OMNI MOTHER: Zig System Allocator for MoE
// No-undefined-behavior system programming

pub const OmniMoEAllocator = struct {
    backing_allocator: std.mem.Allocator,

    pub fn init(allocator: std.mem.Allocator) OmniMoEAllocator {
        return .{ .backing_allocator = allocator };
    }

    pub fn allocateTensorBuffer(self: *OmniMoEAllocator, size: usize) ![]u8 {
        return self.backing_allocator.alloc(u8, size);
    }

    pub fn freeTensorBuffer(self: *OmniMoEAllocator, buffer: []u8) void {
        self.backing_allocator.free(buffer);
    }
};
