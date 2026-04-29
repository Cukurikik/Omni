// OMNI System Layer - ChatTTS Audio Buffer
const std = @import("std");

pub const BufferError = error{ BufferFull };

pub const Result = union(enum) {
    Ok: usize,
    Err: BufferError,
};

pub fn push_audio_chunk(buffer: []f32, chunk: []const f32, offset: usize) Result {
    if (offset + chunk.len > buffer.len) {
        return Result{ .Err = BufferError.BufferFull };
    }
    
    std.mem.copy(f32, buffer[offset..], chunk);
    return Result{ .Ok = offset + chunk.len };
}
