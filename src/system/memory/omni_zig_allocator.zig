const std = @import("std");

/// Omni Zig Arena Allocator (Zig)
/// System & Memory Layer
/// Provides a fast, bump-pointer arena allocator for throwing away
/// short-lived intermediate activation tensors during transformer inference.
/// Avoids system call overheads during individual token generation.

pub const OmniArena = struct {
    buffer: []u8,
    offset: usize,

    pub fn init(buffer: []u8) OmniArena {
        return OmniArena{
            .buffer = buffer,
            .offset = 0,
        };
    }

    /// Implement the Zig Allocator interface
    pub fn allocator(self: *OmniArena) std.mem.Allocator {
        return std.mem.Allocator{
            .ptr = self,
            .vtable = &.{
                .alloc = alloc,
                .resize = resize,
                .free = free,
            },
        };
    }

    fn alloc(ctx: *anyopaque, len: usize, ptr_align: u8, ret_addr: usize) ?[*]u8 {
        _ = ret_addr;
        var self: *OmniArena = @ptrCast(@alignCast(ctx));
        
        // Align offset
        const alignment = @as(usize, 1) << @as(std.mem.Allocator.Log2Align, @intCast(ptr_align));
        const aligned_offset = std.mem.alignForward(usize, self.offset, alignment);
        
        const new_offset = aligned_offset + len;
        if (new_offset > self.buffer.len) {
            return null; // Out of memory in this arena
        }
        
        self.offset = new_offset;
        return self.buffer.ptr + aligned_offset;
    }

    fn resize(ctx: *anyopaque, buf: []u8, buf_align: u8, new_len: usize, ret_addr: usize) bool {
        _ = ctx; _ = buf; _ = buf_align; _ = new_len; _ = ret_addr;
        // Bump allocators generally do not resize efficiently
        return false;
    }

    fn free(ctx: *anyopaque, buf: []u8, buf_align: u8, ret_addr: usize) void {
        _ = ctx; _ = buf; _ = buf_align; _ = ret_addr;
        // Freeing individual items is a no-op in a bump arena.
        // The entire arena is reset at once via `reset()`.
    }

    pub fn reset(self: *OmniArena) void {
        self.offset = 0;
    }
};
