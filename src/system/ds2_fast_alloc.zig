// OMNI System Layer - DS2 Fast Alloc
const std = @import("std");

pub const AllocError = error{ OutOfMemory, InvalidSize };

pub const Result = union(enum) {
    Ok: []u8,
    Err: AllocError,
};

pub fn allocate_rating_buffer(allocator: std.mem.Allocator, size: usize) Result {
    if (size == 0) {
        return Result{ .Err = AllocError.InvalidSize };
    }
    
    const buffer = allocator.alloc(u8, size) catch {
        return Result{ .Err = AllocError.OutOfMemory };
    };
    
    return Result{ .Ok = buffer };
}

pub fn free_rating_buffer(allocator: std.mem.Allocator, buffer: []u8) void {
    allocator.free(buffer);
}
