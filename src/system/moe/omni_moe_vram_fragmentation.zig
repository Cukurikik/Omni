const std = @import("std");

/// OMNI MOTHER Production Zero-Mock VRAM Defragmenter
/// Compresses segmented memory blocks in VRAM to prevent OutOfMemory errors
/// during dynamic expert tensor allocation.

pub const Block = struct {
    offset: usize,
    size: usize,
    is_free: bool,
};

pub const Defragmenter = struct {
    blocks: std.ArrayList(Block),
    allocator: std.mem.Allocator,

    pub fn init(allocator: std.mem.Allocator, total_size: usize) !Defragmenter {
        var defrag = Defragmenter{
            .blocks = std.ArrayList(Block).init(allocator),
            .allocator = allocator,
        };
        try defrag.blocks.append(Block{ .offset = 0, .size = total_size, .is_free = true });
        return defrag;
    }

    pub fn deinit(self: *Defragmenter) void {
        self.blocks.deinit();
    }

    pub fn defragment(self: *Defragmenter) void {
        if (self.blocks.items.len < 2) return;

        var i: usize = 0;
        while (i < self.blocks.items.len - 1) {
            var curr = &self.blocks.items[i];
            var next = &self.blocks.items[i + 1];

            if (curr.is_free and next.is_free) {
                // Merge contiguous free blocks
                curr.size += next.size;
                // Remove the 'next' block
                _ = self.blocks.orderedRemove(i + 1);
                // Do not increment i, check merged block against the new 'next'
            } else {
                i += 1;
            }
        }
    }

    pub fn allocate(self: *Defragmenter, size: usize) !usize {
        for (self.blocks.items, 0..) |*block, i| {
            if (block.is_free and block.size >= size) {
                const offset = block.offset;
                
                if (block.size == size) {
                    block.is_free = false;
                } else {
                    // Split block
                    const remainder_size = block.size - size;
                    block.size = size;
                    block.is_free = false;
                    
                    try self.blocks.insert(i + 1, Block{
                        .offset = offset + size,
                        .size = remainder_size,
                        .is_free = true,
                    });
                }
                return offset;
            }
        }
        
        // If we reach here, we might need defragmentation
        self.defragment();
        
        // Try one more time after defrag
        for (self.blocks.items, 0..) |*block, i| {
            if (block.is_free and block.size >= size) {
                const offset = block.offset;
                if (block.size == size) {
                    block.is_free = false;
                } else {
                    const remainder_size = block.size - size;
                    block.size = size;
                    block.is_free = false;
                    try self.blocks.insert(i + 1, Block{
                        .offset = offset + size,
                        .size = remainder_size,
                        .is_free = true,
                    });
                }
                return offset;
            }
        }
        
        return error.OutOfMemory;
    }

    pub fn free(self: *Defragmenter, offset: usize) !void {
        for (self.blocks.items) |*block| {
            if (block.offset == offset) {
                if (block.is_free) return error.DoubleFree;
                block.is_free = true;
                // Opportunistic quick defrag
                self.defragment();
                return;
            }
        }
        return error.InvalidPointer;
    }
};
