// OMNI System Layer - PaiPai Socket Buffer
const std = @import("std");

pub const SocketError = error{ BufferOverflow, InvalidPacket };

pub const Result = union(enum) {
    Ok: usize,
    Err: SocketError,
};

pub fn write_socket_packet(buffer: []u8, data: []const u8) Result {
    if (data.len > buffer.len) {
        return Result{ .Err = SocketError.BufferOverflow };
    }
    
    std.mem.copy(u8, buffer, data);
    return Result{ .Ok = data.len };
}
