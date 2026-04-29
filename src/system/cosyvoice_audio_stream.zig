// OMNI System Layer - CosyVoice Audio Stream
const std = @import("std");

pub const StreamError = error{ BufferUnderrun };

pub const Result = union(enum) {
    Ok: usize,
    Err: StreamError,
};

pub fn read_audio_stream(out_buffer: []f32, stream_ptr: [*]const f32, bytes_to_read: usize) Result {
    if (bytes_to_read > out_buffer.len) {
        return Result{ .Err = StreamError.BufferUnderrun };
    }
    
    // Zig memory copy for realtime audio output
    std.mem.copy(f32, out_buffer, stream_ptr[0..bytes_to_read]);
    return Result{ .Ok = bytes_to_read };
}
