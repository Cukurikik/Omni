const std = @import("std");

// bert4torch Attention Score Buffer
// Zero-copy attention computation buffer with strict dimension limits

pub const OmniError = error{ DimOverflow, AllocationFailed, InvalidHead };

pub fn OmniResult(comptime T: type) type {
    return union(enum) { Ok: T, Err: OmniError };
}

pub const AttentionBuffer = struct {
    scores: []f32,
    num_heads: u32,
    seq_len: u32,
    head_dim: u32,
    allocator: std.mem.Allocator,

    const MAX_HEADS: u32 = 128;
    const MAX_SEQ: u32 = 32768;
    const MAX_HEAD_DIM: u32 = 256;

    pub fn init(alloc: std.mem.Allocator, heads: u32, seq: u32, dim: u32) OmniResult(AttentionBuffer) {
        if (heads > MAX_HEADS) return OmniResult(AttentionBuffer){ .Err = OmniError.DimOverflow };
        if (seq > MAX_SEQ) return OmniResult(AttentionBuffer){ .Err = OmniError.DimOverflow };
        if (dim > MAX_HEAD_DIM) return OmniResult(AttentionBuffer){ .Err = OmniError.DimOverflow };

        const total = @as(usize, heads) * seq * seq;
        const buf = alloc.alloc(f32, total) catch {
            return OmniResult(AttentionBuffer){ .Err = OmniError.AllocationFailed };
        };
        return OmniResult(AttentionBuffer){ .Ok = AttentionBuffer{
            .scores = buf, .num_heads = heads, .seq_len = seq, .head_dim = dim, .allocator = alloc,
        }};
    }

    pub fn deinit(self: *AttentionBuffer) void {
        self.allocator.free(self.scores);
    }
};
