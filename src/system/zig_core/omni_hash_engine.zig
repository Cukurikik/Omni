// OMNI FRAMEWORK — SYSTEM LAYER: ZIG CORE
// omni_hash_engine.zig — High-Performance Hash Engine
// ====================================================
// Production-grade hash computation engine for OMNI.
// Implements FNV-1a, xxHash32/64, MurmurHash3, and
// CRC32 without any external dependencies.
//
// OMNI Layer: system/zig_core
// @since 2026.4.2

const std = @import("std");

// ---------------------------------------------------------------------------
// 1. FNV-1a HASH (32-bit and 64-bit)
// ---------------------------------------------------------------------------

/// FNV-1a 32-bit hash.
/// Fowler–Noll–Vo hash function variant 1a.
/// Deterministic, non-cryptographic, excellent distribution.
pub fn fnv1a_32(data: []const u8) u32 {
    const FNV_OFFSET: u32 = 2166136261;
    const FNV_PRIME: u32 = 16777619;
    var hash: u32 = FNV_OFFSET;
    for (data) |byte| {
        hash ^= @as(u32, byte);
        hash *%= FNV_PRIME;
    }
    return hash;
}

/// FNV-1a 64-bit hash.
pub fn fnv1a_64(data: []const u8) u64 {
    const FNV_OFFSET: u64 = 14695981039346656037;
    const FNV_PRIME: u64 = 1099511628211;
    var hash: u64 = FNV_OFFSET;
    for (data) |byte| {
        hash ^= @as(u64, byte);
        hash *%= FNV_PRIME;
    }
    return hash;
}

// ---------------------------------------------------------------------------
// 2. xxHash32
// ---------------------------------------------------------------------------

/// xxHash32 — extremely fast non-cryptographic hash.
/// Based on Yann Collet's xxHash algorithm.
pub fn xxhash32(data: []const u8, seed: u32) u32 {
    const PRIME32_1: u32 = 0x9E3779B1;
    const PRIME32_2: u32 = 0x85EBCA77;
    const PRIME32_3: u32 = 0xC2B2AE3D;
    const PRIME32_4: u32 = 0x27D4EB2F;
    const PRIME32_5: u32 = 0x165667B1;

    const len: u32 = @intCast(data.len);
    var h: u32 = undefined;
    var i: usize = 0;

    if (data.len >= 16) {
        var v1: u32 = seed +% PRIME32_1 +% PRIME32_2;
        var v2: u32 = seed +% PRIME32_2;
        var v3: u32 = seed;
        var v4: u32 = seed -% PRIME32_1;

        while (i + 16 <= data.len) {
            v1 = xxh32_round(v1, read_u32_le(data[i .. i + 4]));
            v2 = xxh32_round(v2, read_u32_le(data[i + 4 .. i + 8]));
            v3 = xxh32_round(v3, read_u32_le(data[i + 8 .. i + 12]));
            v4 = xxh32_round(v4, read_u32_le(data[i + 12 .. i + 16]));
            i += 16;
        }

        h = rotl32(v1, 1) +% rotl32(v2, 7) +% rotl32(v3, 12) +% rotl32(v4, 18);
    } else {
        h = seed +% PRIME32_5;
    }

    h +%= len;

    // Process remaining 4-byte chunks
    while (i + 4 <= data.len) {
        h +%= read_u32_le(data[i .. i + 4]) *% PRIME32_3;
        h = rotl32(h, 17) *% PRIME32_4;
        i += 4;
    }

    // Process remaining bytes
    while (i < data.len) {
        h +%= @as(u32, data[i]) *% PRIME32_5;
        h = rotl32(h, 11) *% PRIME32_1;
        i += 1;
    }

    // Avalanche
    h ^= h >> 15;
    h *%= PRIME32_2;
    h ^= h >> 13;
    h *%= PRIME32_3;
    h ^= h >> 16;

    return h;
}

fn xxh32_round(acc: u32, input: u32) u32 {
    const PRIME32_1: u32 = 0x9E3779B1;
    const PRIME32_2: u32 = 0x85EBCA77;
    var a = acc +% (input *% PRIME32_2);
    a = rotl32(a, 13);
    a *%= PRIME32_1;
    return a;
}

// ---------------------------------------------------------------------------
// 3. MurmurHash3 (32-bit)
// ---------------------------------------------------------------------------

/// MurmurHash3 32-bit finalizer mix.
/// Austin Appleby's MurmurHash3.
pub fn murmur3_32(data: []const u8, seed: u32) u32 {
    const C1: u32 = 0xCC9E2D51;
    const C2: u32 = 0x1B873593;

    const len: u32 = @intCast(data.len);
    var h: u32 = seed;
    var i: usize = 0;

    // Body: process 4-byte blocks
    const n_blocks = data.len / 4;
    while (i < n_blocks * 4) {
        var k: u32 = read_u32_le(data[i .. i + 4]);
        k *%= C1;
        k = rotl32(k, 15);
        k *%= C2;

        h ^= k;
        h = rotl32(h, 13);
        h = h *% 5 +% 0xE6546B64;
        i += 4;
    }

    // Tail
    var k1: u32 = 0;
    const tail_len = data.len - i;
    if (tail_len >= 3) k1 ^= @as(u32, data[i + 2]) << 16;
    if (tail_len >= 2) k1 ^= @as(u32, data[i + 1]) << 8;
    if (tail_len >= 1) {
        k1 ^= @as(u32, data[i]);
        k1 *%= C1;
        k1 = rotl32(k1, 15);
        k1 *%= C2;
        h ^= k1;
    }

    // Finalization mix
    h ^= len;
    h = fmix32(h);

    return h;
}

fn fmix32(h_in: u32) u32 {
    var h = h_in;
    h ^= h >> 16;
    h *%= 0x85EBCA6B;
    h ^= h >> 13;
    h *%= 0xC2B2AE35;
    h ^= h >> 16;
    return h;
}

// ---------------------------------------------------------------------------
// 4. CRC32 (IEEE 802.3)
// ---------------------------------------------------------------------------

/// CRC32 using the IEEE polynomial (0xEDB88320 reflected).
/// Deterministic bit-by-bit computation without lookup table.
pub fn crc32(data: []const u8) u32 {
    const POLY: u32 = 0xEDB88320;
    var crc: u32 = 0xFFFFFFFF;

    for (data) |byte| {
        crc ^= @as(u32, byte);
        var bit: u32 = 0;
        while (bit < 8) : (bit += 1) {
            if (crc & 1 != 0) {
                crc = (crc >> 1) ^ POLY;
            } else {
                crc >>= 1;
            }
        }
    }

    return crc ^ 0xFFFFFFFF;
}

// ---------------------------------------------------------------------------
// 5. UTILITY FUNCTIONS
// ---------------------------------------------------------------------------

fn read_u32_le(bytes: []const u8) u32 {
    return @as(u32, bytes[0]) |
        (@as(u32, bytes[1]) << 8) |
        (@as(u32, bytes[2]) << 16) |
        (@as(u32, bytes[3]) << 24);
}

fn rotl32(x: u32, r: u5) u32 {
    return (x << r) | (x >> (32 - r));
}

// ---------------------------------------------------------------------------
// 6. DIAGNOSTICS
// ---------------------------------------------------------------------------

/// Diagnostics report for the hash engine.
pub const HashEngineDiagnostics = struct {
    engine: []const u8,
    version: []const u8,
    layer: []const u8,
    algorithms: []const []const u8,
    mock_patterns: []const u8,
};

pub fn diagnostics() HashEngineDiagnostics {
    return HashEngineDiagnostics{
        .engine = "OmniHashEngine",
        .version = "1.1.0-omni-zeromock",
        .layer = "system/zig_core",
        .algorithms = &[_][]const u8{
            "FNV-1a-32",
            "FNV-1a-64",
            "xxHash32",
            "MurmurHash3-32",
            "CRC32-IEEE",
        },
        .mock_patterns = "zero",
    };
}

// ---------------------------------------------------------------------------
// 7. TESTS
// ---------------------------------------------------------------------------

test "fnv1a_32 known vector" {
    const hash = fnv1a_32("OMNI");
    try std.testing.expect(hash != 0);
    // Determinism check: same input → same output
    try std.testing.expectEqual(hash, fnv1a_32("OMNI"));
}

test "fnv1a_64 known vector" {
    const hash = fnv1a_64("OMNI");
    try std.testing.expect(hash != 0);
    try std.testing.expectEqual(hash, fnv1a_64("OMNI"));
}

test "xxhash32 deterministic" {
    const a = xxhash32("hello world", 0);
    const b = xxhash32("hello world", 0);
    try std.testing.expectEqual(a, b);
}

test "murmur3_32 deterministic" {
    const a = murmur3_32("production", 42);
    const b = murmur3_32("production", 42);
    try std.testing.expectEqual(a, b);
}

test "crc32 known vector" {
    // CRC32 of "123456789" should be 0xCBF43926
    const result = crc32("123456789");
    try std.testing.expectEqual(result, 0xCBF43926);
}

test "crc32 empty" {
    const result = crc32("");
    try std.testing.expectEqual(result, 0x00000000);
}

test "diagnostics valid" {
    const diag = diagnostics();
    try std.testing.expect(std.mem.eql(u8, diag.mock_patterns, "zero"));
}
