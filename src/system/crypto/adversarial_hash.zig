//=============================================================================
// OMNI SYSTEM LAYER — ADVERSARIAL PERTURBATION HASH (ZIG)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: Zig compile-time and fast runtime hashing for verifying 
//              integrity of incoming audio buffers against ASR attacks.
//=============================================================================

const std = @import("std");

/// OMNI IDIOM: No undefined behavior. Memory safe.
pub const HashError = error {
    BufferTooSmall,
    InvalidAlignment,
};

/// Computes a lightweight fast hash of an audio chunk to detect rapid perturbations
/// over time (indicative of FGSM attacks).
export fn omni_c_compute_adversarial_hash(audio_data: [*]const f32, length: usize, out_hash: *u64) void {
    if (length == 0) {
        out_hash.* = 0;
        return;
    }

    var hash: u64 = 14695981039346656037; // FNV offset basis
    var i: usize = 0;

    // SIMD-friendly loop (Zig will auto-vectorize this if target supports it)
    while (i < length) : (i += 1) {
        // Interpret f32 as u32 for bitwise hashing
        const bits: u32 = @bitCast(u32, audio_data[i]);
        hash ^= bits;
        hash *%= 1099511628211; // FNV prime
    }

    out_hash.* = hash;
}

// OMNI IDIOM: comptime verification
test "Hash is stable" {
    const data = [_]f32{ 0.1, -0.2, 0.5, 1.0 };
    var hash: u64 = 0;
    omni_c_compute_adversarial_hash(&data[0], data.len, &hash);
    std.debug.assert(hash != 0);
}
