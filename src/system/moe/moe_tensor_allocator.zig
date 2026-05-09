// moe_tensor_allocator.zig — System / Memory
// Layer: System / GPU — MoE Arena Allocator
//
// Fast arena allocator specifically designed for transient MoE tensor
// allocations. Prevents memory fragmentation during dynamic expert
// routing by managing fixed-size blocks and cache-aligned buffers.

const std = @import("std");

pub const TensorAllocatorError = error{
    OutOfMemory,
    InvalidAlignment,
    BlockTooSmall,
};

/// A block of memory within the arena.
const Block = struct {
    data: []u8,
    used: usize,
    next: ?*Block,
};

/// Arena allocator optimized for MoE transient tensors.
pub struct MoETensorArena {
    backing_allocator: std.mem.Allocator,
    block_size: usize,
    head: ?*Block,
    alignment: usize,

    pub fn init(allocator: std.mem.Allocator, block_size: usize, alignment: usize) MoETensorArena {
        return MoETensorArena{
            .backing_allocator = allocator,
            .block_size = block_size,
            .head = null,
            .alignment = alignment,
        };
    }

    pub fn deinit(self: *MoETensorArena) void {
        var current = self.head;
        while (current) |blk| {
            const next = blk.next;
            self.backing_allocator.free(blk.data);
            self.backing_allocator.destroy(blk);
            current = next;
        }
        self.head = null;
    }

    /// Allocates memory for a tensor. Fast path bumps pointer in current block.
    pub fn alloc(self: *MoETensorArena, size: usize) TensorAllocatorError![]u8 {
        // Ensure aligned size
        const aligned_size = std.mem.alignForward(usize, size, self.alignment);

        // Try to allocate from the current head block
        if (self.head) |head| {
            const remaining = head.data.len - head.used;
            if (remaining >= aligned_size) {
                const ptr = head.data[head.used .. head.used + size];
                head.used += aligned_size;
                return ptr;
            }
        }

        // Need a new block
        const new_block_size = @max(self.block_size, aligned_size);
        const new_data = self.backing_allocator.alloc(u8, new_block_size) catch return error.OutOfMemory;
        
        const new_block = self.backing_allocator.create(Block) catch {
            self.backing_allocator.free(new_data);
            return error.OutOfMemory;
        };

        new_block.* = Block{
            .data = new_data,
            .used = aligned_size,
            .next = self.head,
        };
        self.head = new_block;

        return new_data[0..size];
    }

    /// Allocates a typed tensor array.
    pub fn allocTensor(self: *MoETensorArena, comptime T: type, count: usize) TensorAllocatorError![]T {
        const bytes = try self.alloc(count * @sizeOf(T));
        return std.mem.bytesAsSlice(T, @alignCast(bytes));
    }

    /// Resets the arena for the next forward pass. Does not free backing memory.
    pub fn reset(self: *MoETensorArena) void {
        var current = self.head;
        while (current) |blk| {
            blk.used = 0;
            current = blk.next;
        }
    }
}
