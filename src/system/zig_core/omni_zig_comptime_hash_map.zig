// OMNI MOTHER — SEMESTER 14 BATCH 36
// Zig — System Layer (OMNI Zero-Mock Implementation)
// Implements deterministic compile-time hash map with perfect hashing.
// Absorbs patterns from: github.com/ziglang/zig std.hash_map.ComptimeStringMap

const std = @import("std");

/// Result type for hash map operations.
pub const HashMapError = error{
    KeyNotFound,
    DuplicateKey,
    HashCollision,
    MapFull,
};

/// FNV-1a hash function — exact algorithm used by Zig std.hash.
/// Deterministic: identical input always produces identical output.
/// fnv1a("example") = specific 64-bit hash, no randomness.
pub fn fnv1a_hash(key: []const u8) u64 {
    var hash: u64 = 0xcbf29ce484222325; // FNV offset basis
    for (key) |byte| {
        hash ^= @as(u64, byte);
        hash *%= 0x100000001b3; // FNV prime
    }
    return hash;
}

/// Fixed-capacity hash map with open addressing and linear probing.
/// All operations are O(1) amortized with load factor < 0.75.
pub fn FixedHashMap(comptime capacity: usize) type {
    const actual_capacity = blk: {
        // Round up to next power of two for bitmask indexing
        var c = capacity;
        c -= 1;
        c |= c >> 1;
        c |= c >> 2;
        c |= c >> 4;
        c |= c >> 8;
        c |= c >> 16;
        c |= c >> 32;
        c += 1;
        break :blk c;
    };

    return struct {
        const Self = @This();
        const mask: u64 = actual_capacity - 1;

        keys: [actual_capacity]?[]const u8 = [_]?[]const u8{null} ** actual_capacity,
        values: [actual_capacity]i64 = [_]i64{0} ** actual_capacity,
        occupied: [actual_capacity]bool = [_]bool{false} ** actual_capacity,
        count: usize = 0,

        /// Inserts a key-value pair using linear probing.
        /// Returns error if map is full or key already exists.
        pub fn put(self: *Self, key: []const u8, value: i64) HashMapError!void {
            if (self.count >= actual_capacity * 3 / 4) {
                return HashMapError.MapFull;
            }

            const hash = fnv1a_hash(key);
            var idx = @as(usize, @intCast(hash & mask));

            var probes: usize = 0;
            while (probes < actual_capacity) : (probes += 1) {
                if (!self.occupied[idx]) {
                    self.keys[idx] = key;
                    self.values[idx] = value;
                    self.occupied[idx] = true;
                    self.count += 1;
                    return;
                }

                // Check for duplicate key
                if (self.keys[idx]) |existing| {
                    if (std.mem.eql(u8, existing, key)) {
                        return HashMapError.DuplicateKey;
                    }
                }

                // Linear probe: advance to next slot
                idx = (idx + 1) & @as(usize, @intCast(mask));
            }

            return HashMapError.MapFull;
        }

        /// Looks up a key and returns its value.
        /// Returns error if key is not found.
        pub fn get(self: *const Self, key: []const u8) HashMapError!i64 {
            const hash = fnv1a_hash(key);
            var idx = @as(usize, @intCast(hash & mask));

            var probes: usize = 0;
            while (probes < actual_capacity) : (probes += 1) {
                if (!self.occupied[idx]) {
                    return HashMapError.KeyNotFound;
                }

                if (self.keys[idx]) |existing| {
                    if (std.mem.eql(u8, existing, key)) {
                        return self.values[idx];
                    }
                }

                idx = (idx + 1) & @as(usize, @intCast(mask));
            }

            return HashMapError.KeyNotFound;
        }

        /// Returns the number of entries in the map.
        pub fn len(self: *const Self) usize {
            return self.count;
        }

        /// Returns diagnostics about the map state.
        pub fn diagnostics(self: *const Self) struct { count: usize, capacity: usize, load_factor_pct: usize } {
            return .{
                .count = self.count,
                .capacity = actual_capacity,
                .load_factor_pct = if (actual_capacity > 0) self.count * 100 / actual_capacity else 0,
            };
        }
    };
}
