// moe_token_packing.zig — System / FFI Boundaries
// Layer: System / FFI — MoE Memory Packing
//
// Handles strict memory-safe packing and unpacking of MoE tokens
// crossing the FFI boundary between Python/Go and low-level Zig/C/Rust kernels.
// Prevents undefined behavior and alignment faults.

const std = @import("std");

/// The standard MoE token structure expected by native kernels.
pub const PackedToken = extern struct {
    token_id: i64,          // Original sequence index
    expert_dest: i32,       // Target expert ID
    routing_weight: f32,    // Softmax weight
    _padding: i32,          // 16-byte alignment
    
    // Embeddings follow immediately in memory (handled as flat array)
};

pub const TokenPackError = error {
    BufferTooSmall,
    MisalignedPointer,
    InvalidDimensions,
};

/// Packs a fragmented AOS (Array of Structures) from Python into
/// a strictly aligned SOA (Structure of Arrays) or contiguous block for the kernel.
export fn omni_moe_pack_tokens(
    num_tokens: usize,
    dim: usize,
    src_ids: [*]const i64,
    src_experts: [*]const i32,
    src_weights: [*]const f32,
    src_embeddings: [*]const f32,
    dst_buffer: [*]u8,
    dst_capacity_bytes: usize
) i32 {
    const header_size = @sizeOf(PackedToken);
    const required_bytes = num_tokens * (header_size + (dim * @sizeOf(f32)));

    if (dst_capacity_bytes < required_bytes) {
        return -1; // BufferTooSmall
    }

    // Ensure alignment of destination
    if (@intFromPtr(dst_buffer) % 16 != 0) {
        return -2; // MisalignedPointer
    }

    var offset: usize = 0;

    for (0..num_tokens) |i| {
        // 1. Write Header
        const header_ptr = @as(*PackedToken, @ptrCast(@alignCast(dst_buffer + offset)));
        header_ptr.* = PackedToken{
            .token_id = src_ids[i],
            .expert_dest = src_experts[i],
            .routing_weight = src_weights[i],
            ._padding = 0,
        };
        offset += header_size;

        // 2. Write Embedding Data
        const emb_src = src_embeddings + (i * dim);
        const emb_dst = @as([*]f32, @ptrCast(@alignCast(dst_buffer + offset)));
        
        // Fast SIMD-friendly copy
        @memcpy(emb_dst[0..dim], emb_src[0..dim]);
        
        offset += (dim * @sizeOf(f32));
    }

    return @as(i32, @intCast(required_bytes));
}
