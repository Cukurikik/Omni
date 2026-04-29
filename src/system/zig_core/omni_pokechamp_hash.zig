// Omni PokeChamp Hash (Zig)
// System Layer: Fast game state hashing for minimax caching.
// Ref: sethkarten/pokechamp — ICML 2025
const std = @import("std");
pub fn hash_game_state(data: []const u8) u64 {
    var h: u64 = 14695981039346656037;
    for (data) |b| { h ^= @as(u64, b); h *%= 1099511628211; }
    return h;
}
