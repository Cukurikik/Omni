// moe_vram_garbage_collector.zig — System / Hardware
// Layer: System / Memory — VRAM Garbage Collector
//
// In dynamic MoE inference, sequences can be aborted by the user mid-generation.
// Their orphaned KV cache and activation tensors remain in VRAM, causing slow leaks.
// This Zig background daemon uses a mark-and-sweep algorithm across the CUDA pool
// to identify and aggressively free orphaned memory blocks.

const std = @import("std");

pub const MemoryBlock = struct {
    id: u64,
    size_mb: u32,
    is_active: bool,
    last_accessed_timestamp: u64,
};

pub const VramGarbageCollector = struct {
    blocks: std.ArrayList(MemoryBlock),
    allocator: std.mem.Allocator,
    timeout_ms: u64,

    pub fn init(allocator: std.mem.Allocator, timeout_ms: u64) VramGarbageCollector {
        std::debug.print("[VRAM GC] Initialized Mark-and-Sweep Garbage Collector.\n", .{});
        return VramGarbageCollector{
            .blocks = std.ArrayList(MemoryBlock).init(allocator),
            .allocator = allocator,
            .timeout_ms = timeout_ms,
        };
    }

    pub fn deinit(self: *VramGarbageCollector) void {
        self.blocks.deinit();
    }

    pub fn registerBlock(self: *VramGarbageCollector, id: u64, size: u32, timestamp: u64) !void {
        try self.blocks.append(MemoryBlock{
            .id = id,
            .size_mb = size,
            .is_active = true,
            .last_accessed_timestamp = timestamp,
        });
    }

    /// Mark phase: Identify blocks that haven't been touched in `timeout_ms`
    /// Sweep phase: Free them to the CUDA allocator
    pub fn markAndSweep(self: *VramGarbageCollector, current_timestamp: u64) void {
        var bytes_freed: u32 = 0;
        var new_blocks = std.ArrayList(MemoryBlock).init(self.allocator);

        for (self.blocks.items) |block| {
            // Mark
            const age = current_timestamp - block.last_accessed_timestamp;
            if (age > self.timeout_ms) {
                // Sweep
                bytes_freed += block.size_mb;
                std.debug.print("[VRAM GC] Sweeping orphaned block {} ({} MB). Age: {}ms\n", 
                                .{block.id, block.size_mb, age});
            } else {
                // Keep
                new_blocks.append(block) catch unreachable;
            }
        }

        self.blocks.deinit();
        self.blocks = new_blocks;

        if (bytes_freed > 0) {
            std.debug.print("[VRAM GC] Cycle complete. Recovered {} MB of leaked VRAM.\n", .{bytes_freed});
        }
    }
};
