const std = @import("std");

pub const KVCacheResult = union(enum) {
    ok: *anyopaque,
    err: []const u8,
};

pub fn allocateKVCache(allocator: std.mem.Allocator, size: usize) KVCacheResult {
    const mem = allocator.alloc(u8, size) catch {
        return KVCacheResult{ .err = "OOM" };
    };
    return KVCacheResult{ .ok = mem.ptr };
}
