const std = @import("std");

/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// AES-GCM Galois Field GF(2^128) Multiplication
/// Mathematically evaluates irreducible polynomial reduction required to authenticate ciphertexts in the Galois/Counter Mode.
/// Absorbed from: Cryptographic-Primitives

pub const GfError = error{
    InvalidBlockSize,
};

/// 128-bit block represented as two 64-bit integers.
/// Big-endian representation is standard for GCM.
pub const Block128 = struct {
    high: u64,
    low: u64,
};

pub const GaloisFieldMultiplier = struct {
    
    /// Structurally evaluates multiplication of two 128-bit blocks in GF(2^128).
    /// GCM uses the irreducible polynomial: x^128 + x^7 + x^2 + x + 1.
    /// This is denoted by the constant `R = 0xE1000000000000000000000000000000`.
    pub fn multiply_gf128(x: Block128, y: Block128) Block128 {
        var z = Block128{ .high = 0, .low = 0 };
        var v = Block128{ .high = y.high, .low = y.low };

        // The reduction polynomial constant R (shifted for highest bit alignment)
        const r_high: u64 = 0xE100000000000000;

        // Iterate over 128 bits
        for (0..2) |word_idx| {
            var word = if (word_idx == 0) x.high else x.low;
            
            for (0..64) |bit_idx| {
                _ = bit_idx;
                
                // 1. If the current bit of X is 1, XOR V into Z
                // We check the MSB (bit 63) since GCM considers the leftmost bit as highest.
                if ((word & 0x8000000000000000) != 0) {
                    z.high ^= v.high;
                    z.low ^= v.low;
                }

                // 2. Multiply V by x (right shift by 1)
                const lsb_v = v.low & 1; // Check if the polynomial will overflow
                
                v.low = (v.low >> 1) | ((v.high & 1) << 63);
                v.high = v.high >> 1;

                // 3. Reduction step: if it overflowed, XOR with the irreducible polynomial R
                if (lsb_v != 0) {
                    v.high ^= r_high;
                    // low part of R is 0 in this representation
                }

                // Move to the next bit
                word <<= 1;
            }
        }

        return z;
    }

    /// Computes the GHASH function required for GCM authentication.
    /// Hash(H, A, C) = (A1*H^m ^ A2*H^(m-1) ... ^ C1*H^n ...)
    /// 
    /// @param h_key The 128-bit Hash Key derived from the AES cipher.
    /// @param data The concatenated Authenticated Data and Ciphertext blocks.
    /// @param out_tag The resulting 128-bit authentication tag accumulator.
    pub fn ghash(h_key: Block128, data: []const u8, out_tag: *Block128) !void {
        if (data.len % 16 != 0) return GfError.InvalidBlockSize;

        var y = Block128{ .high = 0, .low = 0 };

        var offset: usize = 0;
        while (offset < data.len) {
            // Read next 128-bit block (Big-Endian)
            const block_high = std.mem.readInt(u64, data[offset..][0..8], .big);
            const block_low = std.mem.readInt(u64, data[offset+8..][0..8], .big);
            
            // Y_i = (Y_{i-1} XOR X_i) * H
            y.high ^= block_high;
            y.low ^= block_low;

            y = multiply_gf128(y, h_key);

            offset += 16;
        }

        out_tag.* = y;
    }
};
