const std = @import("std");

/// OMNI Monadic Result
pub fn OmniResult(comptime T: type) type {
    return union(enum) {
        ok: T,
        err: []const u8,
    };
}

/// Fast FNV-1a hashing for AST Nodes
/// Bounded to prevent excessive CPU usage on deep trees
pub const AstHasher = struct {
    max_depth: usize,

    pub fn init(max_d: usize) AstHasher {
        return .{ .max_depth = max_d };
    }

    pub fn hash_node(self: *const AstHasher, node_data: []const u8, depth: usize) OmniResult(u64) {
        if (depth > self.max_depth) {
            return .{ .err = "OMNI_LIMIT: AST depth exceeds maximum allowed for hashing." };
        }

        var hash: u64 = 14695981039346656037; // FNV offset basis
        
        for (node_data) |byte| {
            hash ^= byte;
            // FNV prime: 1099511628211
            hash = hash *% 1099511628211;
        }

        return .{ .ok = hash };
    }
};
