const std = @import("std");

/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// Kyber Polynomial Vector Compression
/// Evaluates lattice-based compression heuristics mapping high-coefficient polynomials to constrained byte arrays, securing post-quantum ciphertexts.
/// Absorbed from: CRYSTALS-Kyber-PQC

pub const KyberError = error{
    CompressionBoundsMismatch,
    InvalidPolynomialDegree,
};

/// Kyber operates on polynomials of degree 255.
const KYBER_N: usize = 256;

/// Modulus q = 3329. All coefficients are bounded in [0, q-1]
const KYBER_Q: u16 = 3329;

pub const PolyVecCompressor = struct {
    
    /// Structurally compresses a polynomial where coefficients are modulo q.
    /// Formula: Compress_d(x) = round((2^d / q) * x) mod 2^d
    /// 
    /// For Kyber512, d=10 for polyvec in ciphertext.
    /// This means each coefficient [0, 3328] is compressed down to a 10-bit integer [0, 1023].
    pub fn compress_polyvec_d10(poly: []const u16, out_bytes: *[320]u8) !void {
        if (poly.len != KYBER_N) return KyberError.InvalidPolynomialDegree;

        var temp: [KYBER_N]u16 = undefined;

        // 1. Perform Mathematical Compression
        for (0..KYBER_N) |i| {
            // We want to calculate: round((1024 / 3329) * coeff)
            // To do this strictly with integer math to prevent floating point side-channels:
            // (coeff << 10) + (q/2) / q
            
            const coeff: u32 = poly[i];
            const shifted: u32 = coeff << 10;
            const half_q: u32 = KYBER_Q / 2;
            
            const compressed: u16 = @intCast(((shifted + half_q) / KYBER_Q) & 0x3FF); // 0x3FF = 1023 (10 bits)
            temp[i] = compressed;
        }

        // 2. Pack 10-bit integers into 8-bit bytes.
        // 4 coefficients (40 bits) fit perfectly into 5 bytes (40 bits).
        // 256 coefficients / 4 = 64 blocks of 5 bytes = 320 bytes total.
        
        var byte_idx: usize = 0;
        var t_idx: usize = 0;

        while (t_idx < KYBER_N) {
            const t0 = temp[t_idx + 0];
            const t1 = temp[t_idx + 1];
            const t2 = temp[t_idx + 2];
            const t3 = temp[t_idx + 3];

            out_bytes[byte_idx + 0] = @intCast((t0 >> 0) & 0xFF);
            out_bytes[byte_idx + 1] = @intCast(((t0 >> 8) | (t1 << 2)) & 0xFF);
            out_bytes[byte_idx + 2] = @intCast(((t1 >> 6) | (t2 << 4)) & 0xFF);
            out_bytes[byte_idx + 3] = @intCast(((t2 >> 4) | (t3 << 6)) & 0xFF);
            out_bytes[byte_idx + 4] = @intCast((t3 >> 2) & 0xFF);

            byte_idx += 5;
            t_idx += 4;
        }
    }

    /// Structurally decompresses a 320-byte array back into a polynomial vector of degree 255.
    /// Formula: Decompress_d(x) = round((q / 2^d) * x)
    pub fn decompress_polyvec_d10(in_bytes: *const [320]u8, out_poly: []u16) !void {
        if (out_poly.len != KYBER_N) return KyberError.InvalidPolynomialDegree;

        var byte_idx: usize = 0;
        var p_idx: usize = 0;

        while (byte_idx < 320) {
            const b0: u32 = in_bytes[byte_idx + 0];
            const b1: u32 = in_bytes[byte_idx + 1];
            const b2: u32 = in_bytes[byte_idx + 2];
            const b3: u32 = in_bytes[byte_idx + 3];
            const b4: u32 = in_bytes[byte_idx + 4];

            // Reconstruct 10-bit integers
            const t0: u16 = @intCast((b0 >> 0) | ((b1 & 0x03) << 8));
            const t1: u16 = @intCast((b1 >> 2) | ((b2 & 0x0F) << 6));
            const t2: u16 = @intCast((b2 >> 4) | ((b3 & 0x3F) << 4));
            const t3: u16 = @intCast((b3 >> 6) | ((b4 & 0xFF) << 2));

            // Decompress back to modulo q
            out_poly[p_idx + 0] = decompress_single_d10(t0);
            out_poly[p_idx + 1] = decompress_single_d10(t1);
            out_poly[p_idx + 2] = decompress_single_d10(t2);
            out_poly[p_idx + 3] = decompress_single_d10(t3);

            byte_idx += 5;
            p_idx += 4;
        }
    }

    inline fn decompress_single_d10(compressed: u16) u16 {
        // Decompress_10(x) = round((3329 / 1024) * x)
        // Integer math: (x * 3329 + 512) >> 10
        const x: u32 = compressed;
        return @intCast(((x * KYBER_Q) + 512) >> 10);
    }
};
