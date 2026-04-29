// OMNI System Layer - x1 Search Tree Allocator
const std = @import("std");

pub const TreeError = error{ OutOfMemory, NullPointer };

pub const Result = union(enum) {
    Ok: *TreeNode,
    Err: TreeError,
};

pub const TreeNode = struct {
    id: u64,
    visits: u32,
    value: f32,
};

pub fn alloc_tree_node(allocator: std.mem.Allocator, node_id: u64) Result {
    const node = allocator.create(TreeNode) catch {
        return Result{ .Err = TreeError.OutOfMemory };
    };
    node.* = TreeNode{ .id = node_id, .visits = 0, .value = 0.0 };
    return Result{ .Ok = node };
}

pub fn free_tree_node(allocator: std.mem.Allocator, node: *TreeNode) void {
    allocator.destroy(node);
}
