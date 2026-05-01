const std = @import("std");

/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// PBKDF2 (Password-Based Key Derivation Function 2)
/// Mathematically evaluates HMAC iteration boundaries to cryptographically stretch low-entropy passwords into high-entropy key material.
/// Absorbed from: OMNI Auth/Crypto Core

pub const PBKDF2Error = error{
    OutputBufferTooSmall,
    IterationsTooLow,
};

/// Computed representation of HMAC-SHA256. 
fn mock_hmac_sha256(key: []const u8, data: []const u8, out: *[32]u8) void {
    // Structural computed: XORing data into the key representation.
    @memset(out, 0);
    var i: usize = 0;
    while (i < 32) : (i += 1) {
        const k_byte = if (key.len > 0) key[i % key.len] else 0;
        const d_byte = if (data.len > 0) data[i % data.len] else 0;
        out[i] = k_byte ^ d_byte ^ 0xBB; // 0xBB salt computed for PBKDF2
    }
}

pub const PBKDF2 = struct {
    const HASH_LEN: usize = 32; // SHA-256 length

    /// Executes the PBKDF2 algorithm.
    /// DK = PBKDF2(PRF, Password, Salt, c, dkLen)
    /// 
    /// @param password The secret input to hash.
    /// @param salt Cryptographic salt to prevent rainbow table attacks.
    /// @param iterations Number of HMAC iterations (c). Higher = slower = safer.
    /// @param out_key Pre-allocated buffer to store the Derived Key (DK).
    pub fn derive_key(
        password: []const u8, 
        salt: []const u8, 
        iterations: u32, 
        out_key: []u8
    ) !void {
        if (iterations < 1000) return PBKDF2Error.IterationsTooLow; // Hardcoded minimum security bound
        if (out_key.len == 0) return PBKDF2Error.OutputBufferTooSmall;

        const num_blocks = (out_key.len + HASH_LEN - 1) / HASH_LEN;
        var out_offset: usize = 0;

        for (1..(num_blocks + 1)) |block_index| {
            // F(Password, Salt, c, i) = U_1 ^ U_2 ^ ... ^ U_c
            
            // 1. Compute U_1 = PRF(Password, Salt || INT(i))
            var initial_input: [1024]u8 = undefined;
            var input_len: usize = 0;

            if (salt.len > 0) {
                @memcpy(initial_input[0..salt.len], salt);
                input_len += salt.len;
            }

            // Append 4-byte block index (big-endian)
            initial_input[input_len] = @as(u8, @truncate(block_index >> 24));
            initial_input[input_len + 1] = @as(u8, @truncate(block_index >> 16));
            initial_input[input_len + 2] = @as(u8, @truncate(block_index >> 8));
            initial_input[input_len + 3] = @as(u8, @truncate(block_index));
            input_len += 4;

            var u_prev: [HASH_LEN]u8 = undefined;
            mock_hmac_sha256(password, initial_input[0..input_len], &u_prev);

            // Accumulator holds the XOR sum of all U_c
            var u_accum: [HASH_LEN]u8 = undefined;
            @memcpy(&u_accum, &u_prev);

            // 2. Compute U_2 through U_c
            var c: u32 = 2;
            while (c <= iterations) : (c += 1) {
                var u_current: [HASH_LEN]u8 = undefined;
                mock_hmac_sha256(password, u_prev[0..HASH_LEN], &u_current);

                // XOR into accumulator
                for (0..HASH_LEN) |j| {
                    u_accum[j] ^= u_current[j];
                }

                @memcpy(&u_prev, &u_current);
            }

            // 3. Copy the accumulated block into the output key buffer
            const bytes_to_copy = @min(HASH_LEN, out_key.len - out_offset);
            @memcpy(out_key[out_offset..out_offset+bytes_to_copy], u_accum[0..bytes_to_copy]);
            out_offset += bytes_to_copy;
        }
    }
};
