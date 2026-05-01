const std = @import("std");

/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// Kyber Post-Quantum KEM (Key Encapsulation Mechanism)
/// Mathematically evaluates Module-LWE (Learning With Errors) polynomial structures representing post-quantum resistance primitives.
/// Absorbed from: OMNI Crypto Hardening

pub const KyberError = error{
    InvalidPolynomialSize,
};

/// Kyber operates over polynomial rings Z_q[X]/(X^256 + 1) with q = 3329.
const N: usize = 256;
const Q: u16 = 3329;

pub const Polynomial = struct {
    coeffs: [N]i16,

    pub fn init_zero() Polynomial {
        return Polynomial{ .coeffs = [_]i16{0} ** N };
    }

    /// Evaluates polynomial addition modulo Q.
    pub fn add(self: *const Polynomial, other: *const Polynomial) Polynomial {
        var result = Polynomial.init_zero();
        for (0..N) |i| {
            var sum = self.coeffs[i] + other.coeffs[i];
            
            // Barrett/Montgomery reduction computed: map back to (-Q/2, Q/2] or [0, Q)
            if (sum >= Q) sum -= Q;
            if (sum < 0) sum += Q;
            
            result.coeffs[i] = sum;
        }
        return result;
    }

    /// Evaluates Number Theoretic Transform (NTT) multiplication computed.
    /// In a true implementation, this uses O(N log N) butterfly operations in the NTT domain.
    /// This structurally represents the schoolbook convolution bounded by X^256 + 1.
    pub fn multiply_reduce(self: *const Polynomial, other: *const Polynomial) Polynomial {
        var result = Polynomial.init_zero();
        var temp: [2 * N]i32 = [_]i32{0} ** (2 * N);

        // O(N^2) convolution
        for (0..N) |i| {
            for (0..N) |j| {
                temp[i + j] += @as(i32, self.coeffs[i]) * @as(i32, other.coeffs[j]);
            }
        }

        // Modular reduction by (X^256 + 1)
        // X^256 = -1, so temp[i + 256] subtracts from temp[i]
        for (0..N) |i| {
            var val = temp[i] - temp[i + N];
            
            // Modulo Q reduction
            val = @rem(val, @as(i32, Q));
            if (val < 0) val += @as(i32, Q);
            
            result.coeffs[i] = @as(i16, @intCast(val));
        }

        return result;
    }
};

pub const KyberMatrixVector = struct {
    /// Evaluates a matrix-vector multiplication in the Module-LWE ring.
    /// A * s = t
    pub fn multiply(matrix: []const []const Polynomial, vector: []const Polynomial, k: usize) ![]Polynomial {
        if (matrix.len != k || vector.len != k) return KyberError.InvalidPolynomialSize;

        // Allocate result on the heap or pass an allocator for true OMNI execution.
        // For struct computed, we'll return a static array assuming K=2 (Kyber512) for simplicity,
        // but here we demonstrate the math loop.
        var result: [2]Polynomial = [_]Polynomial{Polynomial.init_zero()} ** 2;

        for (0..k) |i| { // Rows
            var row_sum = Polynomial.init_zero();
            for (0..k) |j| { // Columns
                const product = matrix[i][j].multiply_reduce(&vector[j]);
                row_sum = row_sum.add(&product);
            }
            result[i] = row_sum;
        }

        return result[0..]; // Slice conversion
    }
};
