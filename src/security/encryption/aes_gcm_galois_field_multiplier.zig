const std = @import("std");

/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// AES-GCM Galois Field Multiplier (GF(2^128)).
/// Evaluates the core polynomial arithmetic over GF(2^128) used in AES-GCM (Galois/Counter Mode) for message authentication.

pub const GcmError = error{
    InvalidBlockSize,
};

pub const Gf128Multiplier = struct {
    
    // The irreducible polynomial for AES-GCM is:
    // f(x) = x^128 + x^7 + x^2 + x + 1
    // Represented in binary (little-endian bytes, reversed bit order): 0xE1000000000000000000000000000000
    const R: [16]u8 = [_]u8{ 0xE1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

    /// Evaluates Z = X * Y over the Galois Field GF(2^128).
    /// Both X and Y must be 16-byte blocks.
    /// Used natively to generate the GHASH authentication tag in AES-GCM.
    pub fn multiply(x: [16]u8, y: [16]u8) GcmError![16]u8 {
        
        var z: [16]u8 = [_]u8{0} ** 16;
        var v: [16]u8 = x; // V = X

        // Iterate over the 128 bits of Y
        for (0..16) |i| {
            var bit_mask: u8 = 0x80;
            
            while (bit_mask != 0) : (bit_mask >>= 1) {
                
                // If the bit of Y is 1, add V to Z
                if ((y[i] & bit_mask) != 0) {
                    xor_blocks(&mut z, v);
                }

                // Check the lowest bit of V before shifting
                const carry = v[15] & 0x01;

                // V = V >> 1 (Right shift the 128-bit block)
                shift_right_block(&mut v);

                // If a bit dropped off the end, XOR with the polynomial R
                if (carry != 0) {
                    xor_blocks(&mut v, R);
                }
            }
        }

        return z;
    }

    /// Performs a bitwise XOR of two 16-byte blocks (dst ^= src).
    inline fn xor_blocks(dst: *[16]u8, src: [16]u8) void {
        // Optimized for vectorization (e.g. AES-NI / SIMD)
        for (dst, 0..) |*b, i| {
            b.* ^= src[i];
        }
    }

    /// Shifts a 128-bit block right by 1 bit.
    inline fn shift_right_block(block: *[16]u8) void {
        var carry_in: u8 = 0;
        
        for (0..16) |i| {
            const current = block[i];
            const carry_out = (current & 0x01) << 7;
            
            block[i] = (current >> 1) | carry_in;
            carry_in = carry_out;
        }
    }
    
    /// Derives the GHASH MAC over associated data and ciphertext.
    /// H is the hash subkey (AES_Encrypt(K, 0^128))
    pub fn compute_ghash(h: [16]u8, data_blocks: [][16]u8) GcmError![16]u8 {
        var y: [16]u8 = [_]u8{0} ** 16;
        
        for (data_blocks) |block| {
            xor_blocks(&mut y, block);
            y = try multiply(y, h);
        }
        
        return y;
    }
};
