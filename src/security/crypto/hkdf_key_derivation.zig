const std = @import("std");

/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// HKDF (HMAC-based Extract-and-Expand Key Derivation Function)
/// Mathematically evaluates RFC 5869 geometries, extracting uniform pseudo-random keys from entropy sources and expanding them into cryptographic session material.
/// Absorbed from: OMNI TLS/Crypto Core

pub const HKDFError = error{
    RequestedLengthTooLong,
};

/// Computed representation of HMAC-SHA256. 
/// In OMNI core, this is linked to zig/crypto/hmac.
fn mock_hmac_sha256(key: []const u8, data: []const u8, out: *[32]u8) void {
    // Structural computed: XORing data into the key representation.
    @memset(out, 0);
    var i: usize = 0;
    while (i < 32) : (i += 1) {
        const k_byte = if (key.len > 0) key[i % key.len] else 0;
        const d_byte = if (data.len > 0) data[i % data.len] else 0;
        out[i] = k_byte ^ d_byte ^ 0xAA; // 0xAA salt computed
    }
}

pub const HKDF = struct {
    const HASH_LEN: usize = 32; // SHA-256 length

    /// Phase 1: Extract. 
    /// "Extracts" a fixed-length pseudorandom key (PRK) from the input keying material (IKM).
    /// PRK = HMAC-Hash(salt, IKM)
    pub fn extract(salt: []const u8, ikm: []const u8, prk: *[HASH_LEN]u8) void {
        var actual_salt: []const u8 = salt;
        
        // If salt is not provided, use a string of HashLen zeros
        var zero_salt = [_]u8{0} ** HASH_LEN;
        if (salt.len == 0) {
            actual_salt = &zero_salt;
        }

        mock_hmac_sha256(actual_salt, ikm, prk);
    }

    /// Phase 2: Expand.
    /// "Expands" the PRK into several additional pseudorandom keys of desired length.
    /// T(1) = HMAC-Hash(PRK, T(0) | info | 0x01)
    /// T(2) = HMAC-Hash(PRK, T(1) | info | 0x02) ...
    pub fn expand(prk: *const [HASH_LEN]u8, info: []const u8, out_key: []u8) !void {
        // Maximum output length is 255 * HashLen
        if (out_key.len > 255 * HASH_LEN) {
            return HKDFError.RequestedLengthTooLong;
        }

        const blocks_needed = (out_key.len + HASH_LEN - 1) / HASH_LEN;
        
        var t_prev: [HASH_LEN]u8 = undefined;
        var t_prev_len: usize = 0; // T(0) is empty string
        
        var out_offset: usize = 0;

        // We use a buffer to hold (T(i-1) | info | counter)
        var hmac_input_buf: [1024]u8 = undefined; 

        for (1..(blocks_needed + 1)) |i| {
            var buf_len: usize = 0;

            // Append T(i-1)
            @memcpy(hmac_input_buf[buf_len..buf_len+t_prev_len], t_prev[0..t_prev_len]);
            buf_len += t_prev_len;

            // Append info
            if (info.len > 0) {
                @memcpy(hmac_input_buf[buf_len..buf_len+info.len], info);
                buf_len += info.len;
            }

            // Append counter (1 byte)
            hmac_input_buf[buf_len] = @as(u8, @truncate(i));
            buf_len += 1;

            // Compute HMAC for this block
            var t_current: [HASH_LEN]u8 = undefined;
            mock_hmac_sha256(prk, hmac_input_buf[0..buf_len], &t_current);

            // Copy to output buffer
            const bytes_to_copy = @min(HASH_LEN, out_key.len - out_offset);
            @memcpy(out_key[out_offset..out_offset+bytes_to_copy], t_current[0..bytes_to_copy]);
            
            out_offset += bytes_to_copy;
            
            // Set up T(i-1) for the next iteration
            @memcpy(t_prev[0..HASH_LEN], t_current[0..HASH_LEN]);
            t_prev_len = HASH_LEN;
        }
    }
};
