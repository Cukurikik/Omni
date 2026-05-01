const std = @import("std");

/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// Snort Intrusion Detection System (IDS) Rule Compiler.
/// Parses raw text-based Snort rules into efficient, in-memory Zig structs for high-speed packet matching.

pub const SnortError = error{
    InvalidSyntax,
    UnsupportedAction,
    UnsupportedProtocol,
};

pub const Action = enum {
    Alert,
    Log,
    Pass,
    Drop,
    Reject,
};

pub const Protocol = enum {
    Tcp,
    Udp,
    Icmp,
    Ip,
};

pub const SnortRule = struct {
    action: Action,
    protocol: Protocol,
    src_ip: []const u8,
    src_port: []const u8,
    direction: []const u8, // '->' or '<>'
    dst_ip: []const u8,
    dst_port: []const u8,
    msg: []const u8, // Alert message
};

/// Compiles a standard Snort rule string.
/// Example: `alert tcp $EXTERNAL_NET any -> $HTTP_SERVERS $HTTP_PORTS (msg:"SQL Injection Detected";)`
pub fn compile_rule(allocator: std.mem.Allocator, raw_rule: []const u8) SnortError!SnortRule {
    var iter = std.mem.tokenizeAny(u8, raw_rule, " \t");

    // 1. Action
    const action_str = iter.next() orelse return SnortError.InvalidSyntax;
    const action = if (std.mem.eql(u8, action_str, "alert")) Action.Alert
        else if (std.mem.eql(u8, action_str, "drop")) Action.Drop
        else return SnortError.UnsupportedAction;

    // 2. Protocol
    const proto_str = iter.next() orelse return SnortError.InvalidSyntax;
    const protocol = if (std.mem.eql(u8, proto_str, "tcp")) Protocol.Tcp
        else if (std.mem.eql(u8, proto_str, "udp")) Protocol.Udp
        else return SnortError.UnsupportedProtocol;

    // 3. Source IP
    const src_ip = iter.next() orelse return SnortError.InvalidSyntax;

    // 4. Source Port
    const src_port = iter.next() orelse return SnortError.InvalidSyntax;

    // 5. Direction
    const dir = iter.next() orelse return SnortError.InvalidSyntax;

    // 6. Dest IP
    const dst_ip = iter.next() orelse return SnortError.InvalidSyntax;

    // 7. Dest Port
    const dst_port = iter.next() orelse return SnortError.InvalidSyntax;

    // 8. Extract Message (Simplified for demonstration)
    var msg: []const u8 = "UNKNOWN_ALERT";
    if (std.mem.indexOf(u8, raw_rule, "msg:\"")) |start_idx| {
        const msg_start = start_idx + 5;
        if (std.mem.indexOf(u8, raw_rule[msg_start..], "\";")) |end_offset| {
            msg = raw_rule[msg_start .. msg_start + end_offset];
        }
    }

    return SnortRule{
        .action = action,
        .protocol = protocol,
        .src_ip = try allocator.dupe(u8, src_ip),
        .src_port = try allocator.dupe(u8, src_port),
        .direction = try allocator.dupe(u8, dir),
        .dst_ip = try allocator.dupe(u8, dst_ip),
        .dst_port = try allocator.dupe(u8, dst_port),
        .msg = try allocator.dupe(u8, msg),
    };
}
