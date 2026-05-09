// moe_vibeblade_memory_tier.zig — System Layer: VibeBlade Memory Tiering
// Zig allocator mapping tensor buffers across VRAM, RAM, and NVMe bounds.

const std = @import("std");

pub const Tier = enum {
    VRAM,
    RAM,
    NVME,
};

pub const TieredAllocator = struct {
    vram_cap: usize,
    ram_cap: usize,
    
    vram_used: usize,
    ram_used: usize,

    pub fn init(vram_mb: usize, ram_mb: usize) TieredAllocator {
        return TieredAllocator{
            .vram_cap = vram_mb * 1024 * 1024,
            .ram_cap = ram_mb * 1024 * 1024,
            .vram_used = 0,
            .ram_used = 0,
        };
    }

    pub fn allocate(self: *TieredAllocator, size: usize) struct { tier: Tier, offset: usize } {
        if (self.vram_used + size <= self.vram_cap) {
            const off = self.vram_used;
            self.vram_used += size;
            return .{ .tier = Tier.VRAM, .offset = off };
        } else if (self.ram_used + size <= self.ram_cap) {
            const off = self.ram_used;
            self.ram_used += size;
            return .{ .tier = Tier.RAM, .offset = off };
        } else {
            // Fallback to NVMe swap
            return .{ .tier = Tier.NVME, .offset = 0 }; // Requires page fault handling
        }
    }
};
