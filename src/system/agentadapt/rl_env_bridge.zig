const std = @import("std");

pub fn OmniResult(comptime T: type) type {
    return struct {
        value: T,
        error_msg: ?[]const u8,
        is_ok: bool,
    };
}

pub fn step_environment(action: u32) OmniResult(f32) {
    if (action > 100) {
        return .{ .value = 0.0, .error_msg = "Invalid action space", .is_ok = false };
    }
    
    // Zig memory-safe native bridge for Agentic RL environment
    var reward: f32 = 1.0; // Simulated reward calculation
    
    return .{ .value = reward, .error_msg = null, .is_ok = true };
}
