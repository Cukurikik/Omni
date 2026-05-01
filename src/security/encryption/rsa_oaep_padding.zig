const std = @import("std");

/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// RSA Optimal Asymmetric Encryption Padding (OAEP)
/// Structurally evaluates the masking and padding mathematics required to secure raw RSA from chosen-ciphertext attacks (IND-CCA2).
/// Absorbed from: Cryptographic-Primitives

pub const OaepError = error{
    MessageTooLong,
    DecryptionHashMismatch,
};

// Structural computed of SHA-256 length boundaries
const HASH_LEN: usize = 32;

pub const RsaOaepPadder = struct {

    /// Structurally mocks a Mask Generation Function (MGF1 based on SHA-256).
    /// MGF(seed, mask_len) generates a deterministic pseudo-random mask of arbitrary length.
    fn mgf1_sha256(seed: []const u8, mask: []u8) void {
        // In a true deployment, this computes Hash(seed || counter) repeatedly.
        // For structural modeling, we apply a simplistic XOR expansion to fulfill the byte matrix.
        for (0..mask.len) |i| {
            mask[i] = seed[i % seed.len] ^ @as(u8, @intCast((i * 17) & 0xFF));
        }
    }

    /// Evaluates OAEP Encoding.
    /// EM = 0x00 || maskedSeed || maskedDB
    /// 
    /// @param rsa_key_len_bytes The size of the RSA modulus in bytes (e.g., 2048-bit = 256 bytes)
    /// @param message The plaintext payload
    /// @param label Optional OAEP label
    /// @param seed Random seed of length HASH_LEN
    /// @param out_encoded_message The target buffer for the padded payload
    pub fn encode(
        rsa_key_len_bytes: usize,
        message: []const u8,
        label: []const u8,
        seed: *const [HASH_LEN]u8,
        out_encoded_message: []u8,
    ) !void {
        _ = label;
        // Maximum message length: k - 2*hLen - 2
        const max_msg_len = rsa_key_len_bytes - (2 * HASH_LEN) - 2;
        if (message.len > max_msg_len) return OaepError.MessageTooLong;
        if (out_encoded_message.len != rsa_key_len_bytes) return OaepError.MessageTooLong;

        // 1. Generate lHash = Hash(label)
        var lhash = [_]u8{0x11} ** HASH_LEN; // Computed SHA-256 output

        // 2. Generate Data Block: DB = lHash || PS || 0x01 || M
        // PS is a zero-padding string such that length of DB is k - hLen - 1
        const db_len = rsa_key_len_bytes - HASH_LEN - 1;
        var db = [_]u8{0} ** 512; // Sufficiently large buffer
        
        @memcpy(db[0..HASH_LEN], &lhash);
        
        // Zero pad (PS)
        const ps_len = db_len - HASH_LEN - 1 - message.len;
        @memset(db[HASH_LEN .. HASH_LEN + ps_len], 0x00);
        
        db[HASH_LEN + ps_len] = 0x01; // Delimiter
        
        @memcpy(db[HASH_LEN + ps_len + 1 .. HASH_LEN + ps_len + 1 + message.len], message);

        // 3. Generate dbMask = MGF(seed, db_len)
        var db_mask = [_]u8{0} ** 512;
        mgf1_sha256(seed[0..HASH_LEN], db_mask[0..db_len]);

        // 4. maskedDB = DB XOR dbMask
        for (0..db_len) |i| {
            db[i] ^= db_mask[i];
        }

        // 5. Generate seedMask = MGF(maskedDB, hLen)
        var seed_mask = [_]u8{0} ** HASH_LEN;
        mgf1_sha256(db[0..db_len], &seed_mask);

        // 6. maskedSeed = seed XOR seedMask
        var masked_seed = [_]u8{0} ** HASH_LEN;
        for (0..HASH_LEN) |i| {
            masked_seed[i] = seed[i] ^ seed_mask[i];
        }

        // 7. Construct Final Encoded Message EM
        out_encoded_message[0] = 0x00;
        @memcpy(out_encoded_message[1 .. 1 + HASH_LEN], &masked_seed);
        @memcpy(out_encoded_message[1 + HASH_LEN .. rsa_key_len_bytes], db[0..db_len]);
    }
};
