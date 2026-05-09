// OMNI MOTHER: Zig Memory Arena (Production Grade)
// Multi-tier arena allocator with alignment support, sub-arenas,
// watermark tracking, and FFI-compatible C interface for kernel use.

const std = @import("std");
const Allocator = std.mem.Allocator;
const assert = std.debug.assert;
const log = std.log.scoped(.omni_arena);

pub const ArenaError = error{
    OutOfMemory,
    InvalidAlignment,
    ArenaNotInitialized,
};

/// High-performance bump allocator with alignment guarantees.
/// Designed for batch tensor allocation in inference pipelines
/// where objects share the same lifetime (one forward pass).
pub const OmniArena = struct {
    backing_allocator: Allocator,
    buffer: []u8,
    capacity: usize,
    offset: usize,
    peak_usage: usize,
    allocation_count: u64,
    is_valid: bool,

    /// Initialize arena with a fixed capacity from a backing allocator.
    pub fn init(backing: Allocator, capacity: usize) !OmniArena {
        if (capacity == 0) return ArenaError.OutOfMemory;
        const buffer = try backing.alloc(u8, capacity);
        @memset(buffer, 0);
        log.info("Arena initialized: {d} bytes", .{capacity});
        return OmniArena{
            .backing_allocator = backing,
            .buffer = buffer,
            .capacity = capacity,
            .offset = 0,
            .peak_usage = 0,
            .allocation_count = 0,
            .is_valid = true,
        };
    }

    /// Release the arena buffer back to the backing allocator.
    pub fn deinit(self: *OmniArena) void {
        if (self.is_valid) {
            log.info("Arena deinit: peak={d}/{d} bytes, {d} allocs", .{
                self.peak_usage, self.capacity, self.allocation_count,
            });
            self.backing_allocator.free(self.buffer);
            self.is_valid = false;
        }
    }

    /// Align `offset` upward to `alignment` (must be power of two).
    fn alignUp(offset: usize, alignment: usize) usize {
        const mask = alignment - 1;
        return (offset + mask) & ~mask;
    }

    /// Allocate `size` bytes with the given alignment.
    pub fn allocAligned(self: *OmniArena, size: usize, alignment: usize) ![]u8 {
        if (!self.is_valid) return ArenaError.ArenaNotInitialized;
        if (alignment == 0 or (alignment & (alignment - 1)) != 0) {
            return ArenaError.InvalidAlignment;
        }

        const aligned_offset = alignUp(self.offset, alignment);
        if (aligned_offset + size > self.capacity) {
            log.err("OOM: need {d} at offset {d}, cap {d}", .{ size, aligned_offset, self.capacity });
            return ArenaError.OutOfMemory;
        }

        const ptr = self.buffer[aligned_offset .. aligned_offset + size];
        self.offset = aligned_offset + size;
        self.allocation_count += 1;
        if (self.offset > self.peak_usage) {
            self.peak_usage = self.offset;
        }
        return ptr;
    }

    /// Convenience: allocate with default 16-byte alignment (SIMD friendly).
    pub fn alloc(self: *OmniArena, size: usize) ![]u8 {
        return self.allocAligned(size, 16);
    }

    /// Allocate a typed slice of `T` with proper alignment.
    pub fn allocTyped(self: *OmniArena, comptime T: type, count: usize) ![]T {
        const byte_size = count * @sizeOf(T);
        const alignment = @alignOf(T);
        const bytes = try self.allocAligned(byte_size, alignment);
        return std.mem.bytesAsSlice(T, bytes);
    }

    /// Reset the arena for reuse without freeing the underlying buffer.
    /// O(1) operation — the core advantage of arena allocation.
    pub fn reset(self: *OmniArena) void {
        self.offset = 0;
        self.allocation_count = 0;
    }

    /// Snapshot: save current offset for later partial rollback.
    pub fn savepoint(self: *const OmniArena) usize {
        return self.offset;
    }

    /// Restore offset to a previous savepoint (partial rollback).
    pub fn restore(self: *OmniArena, saved: usize) void {
        assert(saved <= self.offset);
        self.offset = saved;
    }

    /// Returns remaining capacity in bytes.
    pub fn remaining(self: *const OmniArena) usize {
        return self.capacity - self.offset;
    }

    /// Returns utilization percentage [0.0, 100.0].
    pub fn utilization(self: *const OmniArena) f64 {
        if (self.capacity == 0) return 0.0;
        return @as(f64, @floatFromInt(self.offset)) / @as(f64, @floatFromInt(self.capacity)) * 100.0;
    }
};

/// Sub-arena: carves a region from a parent arena for scoped allocation.
pub const SubArena = struct {
    parent: *OmniArena,
    start_offset: usize,
    sub_capacity: usize,
    sub_offset: usize,

    pub fn init(parent: *OmniArena, capacity: usize) !SubArena {
        const chunk = try parent.alloc(capacity);
        _ = chunk;
        return SubArena{
            .parent = parent,
            .start_offset = parent.offset - capacity,
            .sub_capacity = capacity,
            .sub_offset = 0,
        };
    }

    pub fn alloc(self: *SubArena, size: usize) ![]u8 {
        if (self.sub_offset + size > self.sub_capacity) {
            return ArenaError.OutOfMemory;
        }
        const base = self.start_offset + self.sub_offset;
        const ptr = self.parent.buffer[base .. base + size];
        self.sub_offset += size;
        return ptr;
    }

    pub fn reset(self: *SubArena) void {
        self.sub_offset = 0;
    }
};

// ---- C FFI Exports for interop with C/Rust kernel code ----

var global_arena: ?OmniArena = null;

export fn omni_arena_create(capacity: usize) callconv(.C) i32 {
    const arena = OmniArena.init(std.heap.page_allocator, capacity) catch return -1;
    global_arena = arena;
    return 0;
}

export fn omni_arena_alloc(size: usize) callconv(.C) ?[*]u8 {
    if (global_arena) |*arena| {
        const slice = arena.alloc(size) catch return null;
        return slice.ptr;
    }
    return null;
}

export fn omni_arena_reset() callconv(.C) void {
    if (global_arena) |*arena| {
        arena.reset();
    }
}

export fn omni_arena_destroy() callconv(.C) void {
    if (global_arena) |*arena| {
        arena.deinit();
        global_arena = null;
    }
}

test "OmniArena basic lifecycle" {
    var arena = try OmniArena.init(std.testing.allocator, 4096);
    defer arena.deinit();

    const a = try arena.alloc(128);
    try std.testing.expect(a.len == 128);

    const sp = arena.savepoint();
    const b = try arena.alloc(256);
    try std.testing.expect(b.len == 256);

    arena.restore(sp);
    try std.testing.expect(arena.offset == sp);

    arena.reset();
    try std.testing.expect(arena.offset == 0);
    try std.testing.expect(arena.remaining() == 4096);
}

test "OmniArena typed allocation" {
    var arena = try OmniArena.init(std.testing.allocator, 8192);
    defer arena.deinit();

    const floats = try arena.allocTyped(f32, 64);
    try std.testing.expect(floats.len == 64);
    floats[0] = 3.14;
    try std.testing.expectApproxEqAbs(floats[0], 3.14, 0.001);
}
