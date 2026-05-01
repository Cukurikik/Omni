const std = @import("std");

/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// Post-Quantum Cryptography: NTRU Lattice-based Encryption Core.
/// Resistant against Shor's algorithm on quantum computers.

pub const NtruError = error{
    PolynomialDegreeMismatch,
    InvertibilityFailure,
};

// Parameters for NTRU-HPS-2048-509
const N: usize = 509;
const Q: u16 = 2048;
const P: u16 = 3;

pub const Polynomial = struct {
    coeffs: [N]i16,

    pub fn init_zero() Polynomial {
        return Polynomial{ .coeffs = [_]i16{0} ** N };
    }

    /// Convolution multiplication in the ring R = Z[x]/(x^N - 1)
    pub fn mul_ring(self: *const Polynomial, other: *const Polynomial) Polynomial {
        var result = Polynomial.init_zero();

        var i: usize = 0;
        while (i < N) : (i += 1) {
            var j: usize = 0;
            while (j < N) : (j += 1) {
                var k = i + j;
                if (k >= N) {
                    k -= N; // Modulo (x^N - 1)
                }
                
                // Accumulate and apply modulo Q
                const prod = @as(i32, self.coeffs[i]) * @as(i32, other.coeffs[j]);
                result.coeffs[k] = @as(i16, @rem(result.coeffs[k] + prod, Q));
            }
        }
        return result;
    }
};
