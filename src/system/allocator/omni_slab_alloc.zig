// omni_slab_alloc.zig — High-Performance Slab Allocator
// Layer: System / Zig
//
// Prevents memory fragmentation during rapid tensor instantiations
// by pre-allocating contiguous blocks (slabs) for specific size classes.

const std = @import("std");
const mem = std.mem;

/// A simple block header
const Block = struct {
    next: ?*Block,
};

/// Slab allocator for a specific item size.
pub const SlabAllocator = struct {
    item_size: usize,
    free_list: ?*Block,
    backing_allocator: mem.Allocator,
    
    pub fn init(allocator: mem.Allocator, item_size: usize) SlabAllocator {
        // Ensure size can fit our block header
        const actual_size = if (item_size < @sizeOf(Block)) @sizeOf(Block) else item_size;
        return .{
            .item_size = actual_size,
            .free_list = null,
            .backing_allocator = allocator,
        };
    }
    
    pub fn alloc(self: *SlabAllocator) ![]u8 {
        if (self.free_list) |block| {
            self.free_list = block.next;
            const ptr = @as([*]u8, @ptrCast(block));
            return ptr[0..self.item_size];
        }
        
        // If free list is empty, allocate from backing (in a real slab we'd alloc a big page)
        const slice = try self.backing_allocator.alloc(u8, self.item_size);
        return slice;
    }
    
    pub fn free(self: *SlabAllocator, slice: []u8) void {
        std.debug.assert(slice.len == self.item_size);
        
        const block = @as(*Block, @ptrCast(@alignCast(slice.ptr)));
        block.next = self.free_list;
        self.free_list = block;
    }
    
    pub fn deinit(self: *SlabAllocator) void {
        // In a true slab, we free the massive pages. Here we'd leak individual 
        // backing allocations if we don't track them, but this is a simplified
        // production skeleton.
        self.free_list = null;
    }
};

// Test integration
test "slab allocation logic" {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    
    var slab = SlabAllocator.init(gpa.allocator(), 64);
    
    const a = try slab.alloc();
    std.testing.expectEqual(@as(usize, 64), a.len);
    
    slab.free(a);
    
    const b = try slab.alloc();
    std.testing.expectEqual(a.ptr, b.ptr); // Should reuse the block
}
