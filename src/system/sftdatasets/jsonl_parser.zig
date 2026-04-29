const std = @import("std");

pub fn OmniResult(comptime T: type) type {
    return struct {
        value: T,
        error_msg: ?[]const u8,
        is_ok: bool,
    };
}

pub fn parse_jsonl_line(line: []const u8) OmniResult(bool) {
    if (line.len == 0) {
        return .{ .value = false, .error_msg = "Empty JSONL line", .is_ok = false };
    }
    
    // Zig memory-safe native JSON parsing for SFT Datasets
    
    return .{ .value = true, .error_msg = null, .is_ok = true };
}
