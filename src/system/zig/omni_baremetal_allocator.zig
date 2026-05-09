// OMNI System — Zig Baremetal Allocator
// No-undefined-behavior memory management for kernel-level operations

const std = @import("std");

pub const OmniBaremetalAllocator = struct {
    buffer: []u8,
    offset: usize,

    pub fn init(buffer: []u8) OmniBaremetalAllocator {
        return OmniBaremetalAllocator{
            .buffer = buffer,
            .offset = 0,
        };
    }

    pub fn allocator(self: *OmniBaremetalAllocator) std.mem.Allocator {
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
        var self = @as(*OmniBaremetalAllocator, @ptrCast(@alignCast(ctx)));
        
        // Calculate alignment
        const alignment = @as(usize, 1) << @as(std.math.Log2Int(usize), @intCast(ptr_align));
        const aligned_offset = std.mem.alignForward(usize, self.offset, alignment);
        
        if (aligned_offset + len > self.buffer.len) {
            return null; // Out of memory
        }

        self.offset = aligned_offset + len;
        return self.buffer[aligned_offset..].ptr;
    }

    fn resize(ctx: *anyopaque, buf: []u8, buf_align: u8, new_len: usize, ret_addr: usize) bool {
        _ = ctx; _ = buf; _ = buf_align; _ = new_len; _ = ret_addr;
        return false; // Resize not supported in simple bump allocator
    }

    fn free(ctx: *anyopaque, buf: []u8, buf_align: u8, ret_addr: usize) void {
        _ = ctx; _ = buf; _ = buf_align; _ = ret_addr;
        // Bump allocator doesn't free individual items
    }
};
