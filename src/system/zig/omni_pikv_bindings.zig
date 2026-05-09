const std = @import("std");

// OMNI MOTHER: Zig Bindings for PiKV
// High-performance system interface

pub const extern "C" fn omni_pikv_allocator_new(total_blocks: u32) *anyopaque;
pub const extern "C" fn omni_pikv_allocator_free(allocator: *anyopaque) void;
pub const extern "C" fn omni_pikv_allocate_block(allocator: *anyopaque) u32;

pub fn initialize_pikv(blocks: u32) *anyopaque {
    return omni_pikv_allocator_new(blocks);
}
