// ===========================================================================
// OMNI COMPTIME ENGINE (SEMESTER 3 — BATCH 38.10)
// ===========================================================================
// Absorbed From  : Zig comptime + @import + errdefer + optional types
// Logic Inherited: Zig / System Layer (Compile-Time Execution & Safety)
// ===========================================================================
//
// By studying Zig's comptime, Mother learned:
//   1. comptime: arbitrary code execution at compile time
//   2. No hidden allocations, no null, no undefined behavior
//   3. errdefer: cleanup runs only when function returns error
//   4. Optional types: ?T replaces null pointers
//   5. Error unions: !T combines error sets with return values

const std = @import("std");
const Allocator = std.mem.Allocator;

// ============================================================
// PART 1: Compile-Time Type Generation
// ============================================================

/// Generate a struct type at compile-time with named fields.
pub fn NamedTuple(comptime fields: anytype) type {
    const field_info = @typeInfo(@TypeOf(fields));
    var struct_fields: [field_info.Struct.fields.len]std.builtin.Type.StructField = undefined;

    inline for (field_info.Struct.fields, 0..) |field, i| {
        struct_fields[i] = .{
            .name = field.name,
            .type = @TypeOf(@field(@TypeOf(fields), field.name)),
            .default_value = null,
            .is_comptime = false,
            .alignment = 0,
        };
    }

    return @Type(.{
        .Struct = .{
            .layout = .auto,
            .fields = &struct_fields,
            .decls = &.{},
            .is_tuple = false,
        },
    });
}

/// Compile-time string hashing (FNV-1a).
pub fn comptimeHash(comptime str: []const u8) u64 {
    comptime {
        var hash: u64 = 0xcbf29ce484222325;
        for (str) |byte| {
            hash ^= @as(u64, byte);
            hash *%= 0x100000001b3;
        }
        return hash;
    }
}

/// Compile-time power of 2 check.
pub fn isPowerOfTwo(comptime n: u64) bool {
    return n > 0 and (n & (n - 1)) == 0;
}

/// Compile-time log2.
pub fn log2(comptime n: u64) u6 {
    comptime {
        var result: u6 = 0;
        var val = n;
        while (val > 1) {
            val >>= 1;
            result += 1;
        }
        return result;
    }
}

// ============================================================
// PART 2: Error Handling (Error Union + errdefer)
// ============================================================

/// OmniError: tagged error set for domain errors.
pub const OmniError = error{
    OutOfMemory,
    InvalidInput,
    NotFound,
    PermissionDenied,
    Timeout,
    ConnectionRefused,
    ParseError,
    Overflow,
};

/// Result type alias.
pub fn Result(comptime T: type) type {
    return OmniError!T;
}

/// Try to parse an integer from a string.
pub fn parseInt(buf: []const u8) Result(i64) {
    if (buf.len == 0) return error.InvalidInput;

    var result: i64 = 0;
    var negative = false;
    var start: usize = 0;

    if (buf[0] == '-') {
        negative = true;
        start = 1;
    }

    for (buf[start..]) |c| {
        if (c < '0' or c > '9') return error.ParseError;
        const digit = @as(i64, c - '0');
        result = std.math.mul(i64, result, 10) catch return error.Overflow;
        result = std.math.add(i64, result, digit) catch return error.Overflow;
    }

    return if (negative) -result else result;
}

// ============================================================
// PART 3: Generic Data Structures
// ============================================================

/// Compile-time sized ring buffer.
pub fn RingBuffer(comptime T: type, comptime capacity: usize) type {
    return struct {
        const Self = @This();

        buffer: [capacity]T = undefined,
        head: usize = 0,
        tail: usize = 0,
        count: usize = 0,
        total_pushes: u64 = 0,
        total_pops: u64 = 0,

        pub fn init() Self {
            return Self{};
        }

        pub fn push(self: *Self, item: T) !void {
            if (self.count >= capacity) return error.Overflow;
            self.buffer[self.tail] = item;
            self.tail = (self.tail + 1) % capacity;
            self.count += 1;
            self.total_pushes += 1;
        }

        pub fn pop(self: *Self) ?T {
            if (self.count == 0) return null;
            const item = self.buffer[self.head];
            self.head = (self.head + 1) % capacity;
            self.count -= 1;
            self.total_pops += 1;
            return item;
        }

        pub fn peek(self: *const Self) ?T {
            if (self.count == 0) return null;
            return self.buffer[self.head];
        }

        pub fn isFull(self: *const Self) bool {
            return self.count >= capacity;
        }

        pub fn isEmpty(self: *const Self) bool {
            return self.count == 0;
        }

        pub fn len(self: *const Self) usize {
            return self.count;
        }
    };
}

/// Compile-time sized static array with bounds checking.
pub fn StaticArray(comptime T: type, comptime max_size: usize) type {
    return struct {
        const Self = @This();

        items: [max_size]T = undefined,
        len: usize = 0,

        pub fn init() Self {
            return Self{};
        }

        pub fn append(self: *Self, item: T) !void {
            if (self.len >= max_size) return error.Overflow;
            self.items[self.len] = item;
            self.len += 1;
        }

        pub fn get(self: *const Self, index: usize) ?T {
            if (index >= self.len) return null;
            return self.items[index];
        }

        pub fn set(self: *Self, index: usize, value: T) !void {
            if (index >= self.len) return error.InvalidInput;
            self.items[index] = value;
        }

        pub fn removeLast(self: *Self) ?T {
            if (self.len == 0) return null;
            self.len -= 1;
            return self.items[self.len];
        }

        pub fn slice(self: *const Self) []const T {
            return self.items[0..self.len];
        }

        pub fn contains(self: *const Self, value: T) bool {
            for (self.items[0..self.len]) |item| {
                if (item == value) return true;
            }
            return false;
        }

        pub fn clear(self: *Self) void {
            self.len = 0;
        }
    };
}

// ============================================================
// PART 4: Bit Manipulation Utilities
// ============================================================

/// Bit set with compile-time known size.
pub fn BitSet(comptime size: usize) type {
    const word_count = (size + 63) / 64;

    return struct {
        const Self = @This();

        words: [word_count]u64 = [_]u64{0} ** word_count,

        pub fn init() Self {
            return Self{};
        }

        pub fn set(self: *Self, bit: usize) void {
            if (bit >= size) return;
            self.words[bit / 64] |= @as(u64, 1) << @intCast(bit % 64);
        }

        pub fn clear(self: *Self, bit: usize) void {
            if (bit >= size) return;
            self.words[bit / 64] &= ~(@as(u64, 1) << @intCast(bit % 64));
        }

        pub fn isSet(self: *const Self, bit: usize) bool {
            if (bit >= size) return false;
            return (self.words[bit / 64] & (@as(u64, 1) << @intCast(bit % 64))) != 0;
        }

        pub fn toggle(self: *Self, bit: usize) void {
            if (bit >= size) return;
            self.words[bit / 64] ^= @as(u64, 1) << @intCast(bit % 64);
        }

        pub fn popCount(self: *const Self) usize {
            var count: usize = 0;
            for (self.words) |word| {
                count += @popCount(word);
            }
            return count;
        }

        pub fn clearAll(self: *Self) void {
            for (&self.words) |*word| {
                word.* = 0;
            }
        }
    };
}

// ============================================================
// Diagnostics
// ============================================================

pub const diagnostics = .{
    .engine = "OmniComptimeEngine",
    .layer = "Zig System",
    .components = .{
        "comptimeHash", "RingBuffer", "StaticArray",
        "BitSet", "Result", "parseInt",
    },
    .learned_logic = .{
        "comptime-arbitrary-execution",
        "error-union-result-type",
        "errdefer-cleanup-on-error",
        "optional-type-null-safety",
        "generic-type-function-param",
        "ring-buffer-modular-index",
        "bitset-word-array-popcount",
        "compile-time-string-hashing",
    },
};
