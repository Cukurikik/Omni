const std = @import("std");

/// OMNI Framework - KV Cache Block Indexer (Zig)
/// Provides ultra-fast, predictable latency indexing for PagedAttention.
/// Written in Zig for extreme memory safety without garbage collection pauses.

pub const Block = struct {
    physical_idx: u32,
    ref_count: u32,
};

pub const KVCacheManager = struct {
    allocator: std.mem.Allocator,
    blocks: []Block,
    free_list: std.ArrayList(u32),

    pub fn init(allocator: std.mem.Allocator, num_blocks: u32) !KVCacheManager {
        var blocks = try allocator.alloc(Block, num_blocks);
        var free_list = std.ArrayList(u32).init(allocator);

        // Initialize blocks and free list
        for (blocks, 0..) |*block, i| {
            block.physical_idx = @intCast(u32, i);
            block.ref_count = 0;
            try free_list.append(@intCast(u32, i));
        }

        std.debug.print("OMNI Zig: Initialized KV Cache Manager with {d} blocks.\n", .{num_blocks});

        return KVCacheManager{
            .allocator = allocator,
            .blocks = blocks,
            .free_list = free_list,
        };
    }

    pub fn allocateBlock(self: *KVCacheManager) ?u32 {
        if (self.free_list.items.len == 0) {
            return null; // OOM
        }
        const idx = self.free_list.pop();
        self.blocks[idx].ref_count = 1;
        return idx;
    }

    pub fn freeBlock(self: *KVCacheManager, physical_idx: u32) !void {
        if (physical_idx >= self.blocks.len) return error.InvalidBlockIndex;
        
        self.blocks[physical_idx].ref_count -= 1;
        if (self.blocks[physical_idx].ref_count == 0) {
            try self.free_list.append(physical_idx);
        }
    }

    pub fn deinit(self: *KVCacheManager) void {
        self.allocator.free(self.blocks);
        self.free_list.deinit();
    }
};

// Test / Export block
// test "KV Allocation" { ... }
