// OMNI System Layer
// Zig Memory Allocator
// Based on ziglang/zig. Implements the foundational memory arena used by the Universal Binary
// to guarantee zero-copy, crash-safe data boundaries.

const std = @import("std");

/// The Omni Arena provides contiguous memory blocks that can be shared across
/// C, Rust, Go, and Python without copying.
pub const OmniMemoryArena = struct {
    allocator: std.mem.Allocator,
    buffer: []u8,
    cursor: usize,

    pub fn init(base_allocator: std.mem.Allocator, size: usize) !OmniMemoryArena {
        std.debug.print("OMNI Zig: Allocating Zero-Copy Universal Arena ({} bytes)\n", .{size});
        
        const buf = try base_allocator.alloc(u8, size);
        return OmniMemoryArena{
            .allocator = base_allocator,
            .buffer = buf,
            .cursor = 0,
        };
    }

    pub fn deinit(self: *OmniMemoryArena) void {
        self.allocator.free(self.buffer);
        std.debug.print("OMNI Zig: Universal Arena Deallocated.\n", .{});
    }

    /// Allocates a contiguous slice of memory, returning a stable pointer 
    /// suitable for FFI (Foreign Function Interface).
    pub fn allocate(self: *OmniMemoryArena, size: usize) ![*]u8 {
        if (self.cursor + size > self.buffer.len) {
            std.debug.print("OMNI Error: Universal Arena Out of Memory (OOM)\n", .{});
            return error.OutOfMemory;
        }

        const ptr = @ptrCast([*]u8, &self.buffer[self.cursor]);
        self.cursor += size;
        return ptr;
    }
    
    pub fn reset(self: *OmniMemoryArena) void {
        self.cursor = 0;
    }
};

// C-ABI Exports for Universal Linkage

var global_arena: ?OmniMemoryArena = null;

export fn omni_zig_arena_init(size: usize) i32 {
    if (global_arena != null) return -1; // Already initialized

    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    const allocator = gpa.allocator();
    
    global_arena = OmniMemoryArena.init(allocator, size) catch {
        return -2; // OOM on init
    };
    return 0; // OK
}

export fn omni_zig_arena_alloc(size: usize) ?[*]u8 {
    if (global_arena) |*arena| {
        return arena.allocate(size) catch null;
    }
    return null;
}

export fn omni_zig_arena_reset() void {
    if (global_arena) |*arena| {
        arena.reset();
    }
}
