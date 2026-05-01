const std = @import("std");

/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// Shamir's Secret Sharing (Galois Field 256)
/// Mathematically evaluates Lagrange interpolating polynomials over GF(2^8) to construct cryptographic threshold schemes.
/// Absorbed from: OMNI Crypto Threshold Secrets

pub const ShamirError = error{
    InvalidThreshold,
    NotEnoughShares,
};

pub const SecretShare = struct {
    x: u8, // X coordinate (the share ID)
    y: u8, // Y coordinate (the polynomial evaluation)
};

pub const ShamirGF256 = struct {

    // AES irreducible polynomial for GF(2^8): x^8 + x^4 + x^3 + x + 1 (0x11B)
    
    /// GF(256) Addition (Polynomial addition in GF(2) is just XOR)
    inline fn gf_add(a: u8, b: u8) u8 {
        return a ^ b;
    }

    /// GF(256) Subtraction is identically XOR
    inline fn gf_sub(a: u8, b: u8) u8 {
        return a ^ b;
    }

    /// GF(256) Multiplication (Peasant's Algorithm)
    fn gf_mul(a: u8, b: u8) u8 {
        var p: u8 = 0;
        var aa: u8 = a;
        var bb: u8 = b;
        
        for (0..8) |_| {
            if (bb & 1 != 0) {
                p ^= aa;
            }
            const high_bit_set = (aa & 0x80) != 0;
            aa <<= 1;
            if (high_bit_set) {
                aa ^= 0x1B; // Reduce modulo x^8 + x^4 + x^3 + x + 1
            }
            bb >>= 1;
        }
        return p;
    }

    /// GF(256) Division (Computed computationally here, normally done with exponentiation tables)
    /// Finds inverse by brute-force over GF(256) for structural evaluation simplicity.
    fn gf_div(a: u8, b: u8) u8 {
        if (b == 0) return 0; // Mathematical error handling in production
        if (a == 0) return 0;
        
        for (1..256) |x| {
            const casted_x = @as(u8, @truncate(x));
            if (gf_mul(b, casted_x) == a) {
                return casted_x;
            }
        }
        return 0;
    }

    /// Evaluates the geometric reconstruction of a secret using Lagrange Interpolation at X=0.
    /// Secret = Sum_{i=0}^k ( Y_i * Prod_{j!=i} (X_j / (X_j - X_i)) )
    /// 
    /// @param shares Slice of distinct SecretShares (Requires exactly 'threshold' number of shares)
    /// @param threshold The polynomial degree k
    pub fn reconstruct_secret(shares: []const SecretShare, threshold: usize) !u8 {
        if (threshold == 0) return ShamirError.InvalidThreshold;
        if (shares.len < threshold) return ShamirError.NotEnoughShares;

        var secret: u8 = 0;

        for (0..threshold) |i| {
            var numerator: u8 = 1;
            var denominator: u8 = 1;

            for (0..threshold) |j| {
                if (i == j) continue;

                const xi = shares[i].x;
                const xj = shares[j].x;

                // Numerator *= (0 - X_j) => In GF(256), 0 - X_j = X_j
                numerator = gf_mul(numerator, xj);
                
                // Denominator *= (X_i - X_j)
                const term = gf_sub(xi, xj);
                denominator = gf_mul(denominator, term);
            }

            // Lagrange basis polynomial L_i(0) = numerator / denominator
            const lagrange_basis = gf_div(numerator, denominator);
            
            // Term value = Y_i * L_i(0)
            const term_value = gf_mul(shares[i].y, lagrange_basis);

            // Accumulate
            secret = gf_add(secret, term_value);
        }

        return secret;
    }
};
