// ===========================================================================
// OMNI ARENA ALLOCATOR ENGINE (SEMESTER 3 REMEDIATION — BATCH 38.1)
// ===========================================================================
// Absorbed From  : std.mem.Allocator + std.heap.ArenaAllocator + mimalloc
// Logic Inherited: Zig / System Layer (Region-Based Arena Allocation)
// Domain Layer   : System (Zig Core)
// ===========================================================================
//
// By studying Zig's std.heap.ArenaAllocator and mimalloc, Mother learned
// that arena allocation provides O(1) alloc and O(1) mass-free:
//   1. All allocations bump a pointer forward in a contiguous buffer
//   2. Individual free is a no-op (memory is released all at once)
//   3. Multiple buffers ("pages") are chained when capacity is exceeded
//   4. Zig's comptime ensures zero-cost generic type safety
//
// Zig IS the language for no-undefined-behavior system programming in OMNI.

const std = @import("std");
const Allocator = std.mem.Allocator;

/// A page in the arena's chain. Each page holds a contiguous buffer.
const ArenaPage = struct {
    buffer: []u8,
    used: usize,
    next: ?*ArenaPage,
};

/// Arena allocator: bump-pointer allocation with mass-free.
///
/// All allocations are served by advancing a cursor in the current page.
/// When the current page is full, a new page is appended.
/// `deinit()` frees ALL pages at once — individual `free` is a no-op.
///
/// This is ideal for request-scoped or frame-scoped allocations where
/// the entire batch of allocations shares the same lifetime.
pub const OmniArenaAllocatorEngine = struct {
    /// The underlying allocator used to obtain pages.
    backing_allocator: Allocator,
    /// Head of the page chain.
    first_page: ?*ArenaPage,
    /// Current page being allocated from.
    current_page: ?*ArenaPage,
    /// Default page size in bytes.
    page_size: usize,

    // Statistics
    total_pages: usize,
    total_bytes_allocated: usize,
    total_alloc_count: usize,
    peak_usage: usize,

    const Self = @This();

    /// Initialize a new arena with the given page size.
    pub fn init(backing: Allocator, page_size: usize) Self {
        return Self{
            .backing_allocator = backing,
            .first_page = null,
            .current_page = null,
            .page_size = page_size,
            .total_pages = 0,
            .total_bytes_allocated = 0,
            .total_alloc_count = 0,
            .peak_usage = 0,
        };
    }

    /// Allocate `n` bytes with the given alignment from the arena.
    /// Returns a slice to the allocated memory.
    pub fn alloc(self: *Self, comptime T: type, n: usize) ![]T {
        const byte_count = @sizeOf(T) * n;
        const alignment = @alignOf(T);

        // Ensure we have a current page with enough space
        if (self.current_page == null) {
            try self.addPage(byte_count);
        }

        var page = self.current_page.?;

        // Align the current offset
        const aligned_used = alignForward(page.used, alignment);
        const end_offset = aligned_used + byte_count;

        if (end_offset > page.buffer.len) {
            // Current page is full — allocate a new one
            const min_size = if (byte_count > self.page_size) byte_count else self.page_size;
            try self.addPage(min_size);
            page = self.current_page.?;
            const new_aligned = alignForward(page.used, alignment);
            page.used = new_aligned + byte_count;
        } else {
            page.used = end_offset;
        }

        // Update statistics
        self.total_bytes_allocated += byte_count;
        self.total_alloc_count += 1;
        if (self.total_bytes_allocated > self.peak_usage) {
            self.peak_usage = self.total_bytes_allocated;
        }

        // Return a typed slice into the page buffer
        const start = alignForward(page.used - byte_count, alignment);
        const raw_ptr = @as([*]T, @ptrCast(@alignCast(page.buffer.ptr + start)));
        return raw_ptr[0..n];
    }

    /// Free is a deliberate no-op in arena allocation.
    /// Memory is only released when `deinit()` is called.
    pub fn free(self: *Self, comptime T: type, ptr: []T) void {
        _ = self;
        _ = ptr;
        // Intentional no-op: arena allocators do not support individual free.
        // All memory is released at once via deinit().
    }

    /// Reset the arena: reuse all pages without freeing them.
    /// Sets all page cursors back to 0.
    pub fn reset(self: *Self) void {
        var page = self.first_page;
        while (page) |p| {
            p.used = 0;
            page = p.next;
        }
        self.current_page = self.first_page;
        self.total_bytes_allocated = 0;
        self.total_alloc_count = 0;
    }

    /// Release ALL memory back to the backing allocator.
    pub fn deinit(self: *Self) void {
        var page = self.first_page;
        while (page) |p| {
            const next = p.next;
            self.backing_allocator.free(p.buffer);
            self.backing_allocator.destroy(p);
            page = next;
        }
        self.first_page = null;
        self.current_page = null;
        self.total_pages = 0;
        self.total_bytes_allocated = 0;
    }

    // ---- Internal ----

    fn addPage(self: *Self, min_size: usize) !void {
        const size = if (min_size > self.page_size) min_size else self.page_size;
        const buffer = try self.backing_allocator.alloc(u8, size);

        const page = try self.backing_allocator.create(ArenaPage);
        page.* = ArenaPage{
            .buffer = buffer,
            .used = 0,
            .next = null,
        };

        // Link to chain
        if (self.current_page) |cur| {
            cur.next = page;
        }
        if (self.first_page == null) {
            self.first_page = page;
        }
        self.current_page = page;
        self.total_pages += 1;
    }

    // ---- Diagnostics ----

    pub const DiagnosticsInfo = struct {
        engine: []const u8,
        layer: []const u8,
        page_size: usize,
        total_pages: usize,
        total_bytes_allocated: usize,
        total_alloc_count: usize,
        peak_usage: usize,
    };

    pub fn diagnostics(self: *const Self) DiagnosticsInfo {
        return DiagnosticsInfo{
            .engine = "OmniArenaAllocatorEngine",
            .layer = "Zig System",
            .page_size = self.page_size,
            .total_pages = self.total_pages,
            .total_bytes_allocated = self.total_bytes_allocated,
            .total_alloc_count = self.total_alloc_count,
            .peak_usage = self.peak_usage,
        };
    }
};

/// Align a value forward to the given alignment.
fn alignForward(addr: usize, alignment: usize) usize {
    const mask = alignment - 1;
    return (addr + mask) & ~mask;
}

// ---- Learned Logic ----
// - bump-pointer-o1-allocation
// - no-op-individual-free
// - page-chain-overflow-handling
// - comptime-generic-type-safety
// - alignment-forward-bitmask
// - region-based-lifetime-management
// - reset-reuse-without-dealloc
