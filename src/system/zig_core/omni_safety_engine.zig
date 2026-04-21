// ===========================================================================
// OMNI SAFETY ENGINE (SEMESTER 3 — BATCH 38.10)
// ===========================================================================
// Absorbed From  : Zig safety features + allocator patterns + sentinel slices
// Logic Inherited: Zig / System Layer (Memory Safety Without GC)
// ===========================================================================
//
// By studying Zig memory safety, Mother learned:
//   1. No hidden control flow (no exceptions, no operator overloading)
//   2. Explicit allocator passing prevents hidden allocation
//   3. Sentinel-terminated slices prevent buffer overruns
//   4. Debug allocator detects use-after-free and double-free
//   5. Testing allocator tracks and validates all allocations

const std = @import("std");
const Allocator = std.mem.Allocator;
const testing = std.testing;

// ============================================================
// PART 1: Tracking Allocator (Leak Detector)
// ============================================================

/// TrackingAllocator: wraps an allocator and tracks all allocations.
pub const TrackingAllocator = struct {
    const Self = @This();

    backing: Allocator,
    total_allocs: u64 = 0,
    total_frees: u64 = 0,
    total_bytes_allocated: u64 = 0,
    total_bytes_freed: u64 = 0,
    peak_bytes: u64 = 0,
    current_bytes: u64 = 0,

    pub fn init(backing: Allocator) Self {
        return Self{
            .backing = backing,
        };
    }

    pub fn allocator(self: *Self) Allocator {
        return .{
            .ptr = self,
            .vtable = &.{
                .alloc = alloc,
                .resize = resize,
                .free = free,
            },
        };
    }

    fn alloc(ctx: *anyopaque, len: usize, ptr_align: u8, ret_addr: usize) ?[*]u8 {
        const self: *Self = @ptrCast(@alignCast(ctx));
        const result = self.backing.rawAlloc(len, ptr_align, ret_addr);
        if (result != null) {
            self.total_allocs += 1;
            self.total_bytes_allocated += len;
            self.current_bytes += len;
            if (self.current_bytes > self.peak_bytes) {
                self.peak_bytes = self.current_bytes;
            }
        }
        return result;
    }

    fn resize(ctx: *anyopaque, buf: []u8, buf_align: u8, new_len: usize, ret_addr: usize) bool {
        const self: *Self = @ptrCast(@alignCast(ctx));
        const result = self.backing.rawResize(buf, buf_align, new_len, ret_addr);
        if (result) {
            if (new_len > buf.len) {
                self.total_bytes_allocated += new_len - buf.len;
                self.current_bytes += new_len - buf.len;
            } else {
                self.total_bytes_freed += buf.len - new_len;
                self.current_bytes -= buf.len - new_len;
            }
            if (self.current_bytes > self.peak_bytes) {
                self.peak_bytes = self.current_bytes;
            }
        }
        return result;
    }

    fn free(ctx: *anyopaque, buf: []u8, buf_align: u8, ret_addr: usize) void {
        const self: *Self = @ptrCast(@alignCast(ctx));
        self.total_frees += 1;
        self.total_bytes_freed += buf.len;
        self.current_bytes -= buf.len;
        self.backing.rawFree(buf, buf_align, ret_addr);
    }

    /// Check for memory leaks.
    pub fn hasLeaks(self: *const Self) bool {
        return self.total_allocs != self.total_frees;
    }

    /// Get leak count.
    pub fn leakCount(self: *const Self) u64 {
        if (self.total_allocs > self.total_frees) {
            return self.total_allocs - self.total_frees;
        }
        return 0;
    }

    /// Report as string.
    pub fn report(self: *const Self) void {
        std.debug.print(
            \\=== Memory Tracking Report ===
            \\Total Allocations:  {}
            \\Total Frees:        {}
            \\Bytes Allocated:    {}
            \\Bytes Freed:        {}
            \\Current Live Bytes: {}
            \\Peak Bytes:         {}
            \\Leak Detected:      {}
            \\
        , .{
            self.total_allocs,
            self.total_frees,
            self.total_bytes_allocated,
            self.total_bytes_freed,
            self.current_bytes,
            self.peak_bytes,
            self.hasLeaks(),
        });
    }
};

// ============================================================
// PART 2: Bounded Buffer (No Overflow)
// ============================================================

/// BoundedBuffer: fixed-capacity buffer that prevents overflow.
pub fn BoundedBuffer(comptime T: type, comptime capacity: usize) type {
    return struct {
        const Self = @This();

        data: [capacity]T = undefined,
        len: usize = 0,

        pub fn init() Self {
            return Self{};
        }

        /// Append item, returns error on overflow.
        pub fn append(self: *Self, item: T) !void {
            if (self.len >= capacity) return error.Overflow;
            self.data[self.len] = item;
            self.len += 1;
        }

        /// Safe access with bounds check.
        pub fn at(self: *const Self, index: usize) !T {
            if (index >= self.len) return error.InvalidInput;
            return self.data[index];
        }

        /// Pop last item.
        pub fn pop(self: *Self) ?T {
            if (self.len == 0) return null;
            self.len -= 1;
            return self.data[self.len];
        }

        /// Iterate over items.
        pub fn items(self: *const Self) []const T {
            return self.data[0..self.len];
        }

        /// Clear all items.
        pub fn reset(self: *Self) void {
            self.len = 0;
        }

        pub fn isFull(self: *const Self) bool {
            return self.len >= capacity;
        }

        pub fn remaining(self: *const Self) usize {
            return capacity - self.len;
        }
    };
}

// ============================================================
// PART 3: Safe String Builder
// ============================================================

/// StringBuilder: dynamically grows string without overflow.
pub const StringBuilder = struct {
    const Self = @This();

    buffer: std.ArrayList(u8),
    total_appends: u64 = 0,

    pub fn init(allocator: Allocator) Self {
        return Self{
            .buffer = std.ArrayList(u8).init(allocator),
        };
    }

    pub fn deinit(self: *Self) void {
        self.buffer.deinit();
    }

    /// Append a string slice.
    pub fn append(self: *Self, str: []const u8) !void {
        try self.buffer.appendSlice(str);
        self.total_appends += 1;
    }

    /// Append a formatted string.
    pub fn appendFmt(self: *Self, comptime fmt: []const u8, args: anytype) !void {
        var writer = self.buffer.writer();
        try writer.print(fmt, args);
        self.total_appends += 1;
    }

    /// Append a single byte.
    pub fn appendByte(self: *Self, byte: u8) !void {
        try self.buffer.append(byte);
    }

    /// Get the built string.
    pub fn toOwnedSlice(self: *Self) ![]u8 {
        return self.buffer.toOwnedSlice();
    }

    /// Get current string view (no ownership transfer).
    pub fn slice(self: *const Self) []const u8 {
        return self.buffer.items;
    }

    /// Current length.
    pub fn len(self: *const Self) usize {
        return self.buffer.items.len;
    }

    /// Clear without freeing.
    pub fn clear(self: *Self) void {
        self.buffer.clearRetainingCapacity();
    }
};

// ============================================================
// PART 4: Resource Guard (Defer / errdefer pattern)
// ============================================================

/// ResourceGuard: RAII-like cleanup using Zig's defer pattern.
pub fn ResourceGuard(comptime T: type) type {
    return struct {
        const Self = @This();

        resource: T,
        cleanup_fn: *const fn (T) void,
        active: bool = true,

        pub fn init(resource: T, cleanup: *const fn (T) void) Self {
            return Self{
                .resource = resource,
                .cleanup_fn = cleanup,
            };
        }

        /// Release without cleanup (take ownership).
        pub fn release(self: *Self) T {
            self.active = false;
            return self.resource;
        }

        /// Manually cleanup early.
        pub fn cleanup(self: *Self) void {
            if (self.active) {
                self.cleanup_fn(self.resource);
                self.active = false;
            }
        }

        /// Access the resource.
        pub fn get(self: *const Self) T {
            return self.resource;
        }
    };
}

// ============================================================
// Diagnostics
// ============================================================

pub const diagnostics = .{
    .engine = "OmniSafetyEngine",
    .layer = "Zig System",
    .components = .{
        "TrackingAllocator", "BoundedBuffer",
        "StringBuilder", "ResourceGuard",
    },
    .learned_logic = .{
        "tracking-allocator-leak-detect",
        "bounded-buffer-no-overflow",
        "explicit-allocator-passing",
        "errdefer-cleanup-on-error",
        "resource-guard-raii-pattern",
        "comptime-generic-type-param",
        "peak-memory-water-mark",
        "safe-string-append-grow",
    },
};
