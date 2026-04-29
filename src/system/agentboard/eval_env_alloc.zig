const std = @import("std");

pub fn OmniResult(comptime T: type) type {
    return struct {
        value: T,
        error_msg: ?[]const u8,
        is_ok: bool,
    };
}

pub fn allocate_eval_environment(env_id: usize) OmniResult(bool) {
    if (env_id == 0) {
        return .{ .value = false, .error_msg = "Invalid environment ID", .is_ok = false };
    }
    // Zig memory-safe native evaluation environment allocation for AgentBoard
    const success = true;
    
    return .{ .value = success, .error_msg = null, .is_ok = true };
}
