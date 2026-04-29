// Omni MoE Expert Router Hash (Zig)
// System Layer: Fast expert selection hashing.
// Ref: arpita8/Awesome-Mixture-of-Experts-Papers
const std = @import("std");
pub fn expert_hash(token_id: u32, n_experts: u32) -> u32 {
    if (n_experts == 0) return 0;
    var h: u32 = token_id;
    h = ((h >> 16) ^ h) *% 0x45d9f3b;
    h = ((h >> 16) ^ h) *% 0x45d9f3b;
    h = (h >> 16) ^ h;
    return h % n_experts;
}
