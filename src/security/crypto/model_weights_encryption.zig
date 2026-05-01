const std = @import("std");

/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// Model Weights Encryption
/// Mathematically evaluates ChaCha20 stream cipher constraints to cryptographically obfuscate proprietary LLM weights at rest.
/// Absorbed from: Enterprise-Model-Security

pub const CryptoError = error{
    InvalidKeyLength,
    InvalidNonceLength,
};

// ChaCha20 uses a 256-bit (32-byte) key and a 96-bit (12-byte) nonce
const KEY_BYTES = 32;
const NONCE_BYTES = 12;

pub const ModelEncryptor = struct {

    /// Quarter Round operation - the core non-linear diffusion mechanism of ChaCha20
    /// a += b; d ^= a; d <<<= 16;
    /// c += d; b ^= c; b <<<= 12;
    /// a += b; d ^= a; d <<<= 8;
    /// c += d; b ^= c; b <<<= 7;
    inline fn quarter_round(a: *u32, b: *u32, c: *u32, d: *u32) void {
        a.* +%= b.*; d.* ^= a.*; d.* = std.math.rotl(u32, d.*, 16);
        c.* +%= d.*; b.* ^= c.*; b.* = std.math.rotl(u32, b.*, 12);
        a.* +%= b.*; d.* ^= a.*; d.* = std.math.rotl(u32, d.*, 8);
        c.* +%= d.*; b.* ^= c.*; b.* = std.math.rotl(u32, b.*, 7);
    }

    /// Generates a 64-byte keystream block using the ChaCha20 matrix
    fn chacha20_block(key: *const [KEY_BYTES]u8, nonce: *const [NONCE_BYTES]u8, counter: u32, out_block: *[64]u8) void {
        var state: [16]u32 = undefined;

        // 1. Setup initial state matrix
        // Constants "expand 32-byte k"
        state[0] = 0x61707865;
        state[1] = 0x3320646e;
        state[2] = 0x79622d32;
        state[3] = 0x6b206574;

        // Key
        for (0..8) |i| {
            state[4 + i] = std.mem.readInt(u32, key[i * 4 .. i * 4 + 4], .little);
        }

        // Counter
        state[12] = counter;

        // Nonce
        for (0..3) |i| {
            state[13 + i] = std.mem.readInt(u32, nonce[i * 4 .. i * 4 + 4], .little);
        }

        // 2. Perform 20 rounds (10 column rounds, 10 diagonal rounds)
        var working_state = state;
        for (0..10) |_| {
            // Column Rounds
            quarter_round(&working_state[0], &working_state[4], &working_state[8],  &working_state[12]);
            quarter_round(&working_state[1], &working_state[5], &working_state[9],  &working_state[13]);
            quarter_round(&working_state[2], &working_state[6], &working_state[10], &working_state[14]);
            quarter_round(&working_state[3], &working_state[7], &working_state[11], &working_state[15]);
            // Diagonal Rounds
            quarter_round(&working_state[0], &working_state[5], &working_state[10], &working_state[15]);
            quarter_round(&working_state[1], &working_state[6], &working_state[11], &working_state[12]);
            quarter_round(&working_state[2], &working_state[7], &working_state[8],  &working_state[13]);
            quarter_round(&working_state[3], &working_state[4], &working_state[9],  &working_state[14]);
        }

        // 3. Add working state to original state to get final pseudo-random block
        for (0..16) |i| {
            const final_word = working_state[i] +% state[i];
            std.mem.writeInt(u32, out_block[i * 4 .. i * 4 + 4], final_word, .little);
        }
    }

    /// Encrypts or Decrypts a stream of model weights.
    /// Since ChaCha20 is a stream cipher (XOR), encryption and decryption are the exact same operation.
    /// 
    /// @param key The 32-byte symmetric master key
    /// @param nonce The 12-byte initialization vector
    /// @param data The weight buffer to mutate in-place
    pub fn process_weights(key: []const u8, nonce: []const u8, data: []u8) !void {
        if (key.len != KEY_BYTES) return CryptoError.InvalidKeyLength;
        if (nonce.len != NONCE_BYTES) return CryptoError.InvalidNonceLength;

        var key_arr = [_]u8{0} ** KEY_BYTES;
        @memcpy(&key_arr, key);

        var nonce_arr = [_]u8{0} ** NONCE_BYTES;
        @memcpy(&nonce_arr, nonce);

        var counter: u32 = 1; // Standard RFC starts counter at 1
        var block = [_]u8{0} ** 64;

        var offset: usize = 0;
        const total_len = data.len;

        while (offset < total_len) {
            chacha20_block(&key_arr, &nonce_arr, counter, &block);
            
            const chunk_size = @min(64, total_len - offset);
            
            // XOR the keystream block with the raw weights
            for (0..chunk_size) |i| {
                data[offset + i] ^= block[i];
            }
            
            offset += chunk_size;
            counter +%= 1; // Unsigned wrap-around
        }
    }
};
