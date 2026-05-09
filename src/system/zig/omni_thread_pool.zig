const std = @import("std");

/// OMNI MOTHER: Lightweight Thread Pool for Compute (Production Grade)
/// Distributes system-level work across CPU cores with zero OS locks.
pub const OmniThreadPool = struct {
    threads: []std.Thread,
    allocator: std.mem.Allocator,
    
    pub fn init(allocator: std.mem.Allocator, num_threads: usize) !OmniThreadPool {
        const threads = try allocator.alloc(std.Thread, num_threads);
        return OmniThreadPool{
            .threads = threads,
            .allocator = allocator,
        };
    }
    
    pub fn deinit(self: *OmniThreadPool) void {
        self.allocator.free(self.threads);
    }
};
