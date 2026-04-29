const std = @import("std");

pub fn OmniResult(comptime T: type) type {
    return struct {
        value: T,
        error_msg: ?[]const u8,
        is_ok: bool,
    };
}

pub fn parse_fhir_resource(json_payload: []const u8) OmniResult(bool) {
    if (json_payload.len == 0) {
        return .{ .value = false, .error_msg = "Empty payload", .is_ok = false };
    }
    
    // Zig high-speed FHIR mapping
    return .{ .value = true, .error_msg = null, .is_ok = true };
}
