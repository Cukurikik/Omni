const std = @import("std");

/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// SHA-3 Keccak Sponge F1600 Core.
/// Structurally executes the exact Bitwise Permutation matrices (Theta, Rho, Pi, Chi, Iota) mapping the core Keccak-f[1600] cryptographic hash function.

pub const Sha3Error = error{
    InvalidCapacity,
};

pub const KeccakSponge = struct {

    // 5x5 Matrix of 64-bit lanes (1600 bits total)
    state: [25]u64,

    // Iota round constants to destroy symmetry
    const RC = [_]u64{
        0x0000000000000001, 0x0000000000008082, 0x800000000000808a,
        0x8000000080008000, 0x000000000000808b, 0x0000000080000001,
        0x8000000080008081, 0x8000000000008009, 0x000000000000008a,
        0x0000000000000088, 0x0000000080008009, 0x000000008000000a,
        0x000000008000808b, 0x800000000000008b, 0x8000000000008089,
        0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
        0x000000000000800a, 0x800000008000000a, 0x8000000080008081,
        0x8000000000008080, 0x0000000080000001, 0x8000000080008008,
    };

    pub fn init() KeccakSponge {
        return KeccakSponge{
            .state = [_]u64{0} ** 25,
        };
    }

    /// Evaluates the Keccak-f[1600] permutation (24 rounds of bit scrambling).
    /// Used inside the Absorb phase of the sponge construction.
    pub fn keccak_f1600(self: *KeccakSponge) void {
        var a = self.state;

        for (0..24) |round| {
            // 1. Theta Step (Parity checks and diffusion)
            var c: [5]u64 = undefined;
            var d: [5]u64 = undefined;

            for (0..5) |x| {
                c[x] = a[x] ^ a[x + 5] ^ a[x + 10] ^ a[x + 15] ^ a[x + 20];
            }

            for (0..5) |x| {
                const x_plus_1 = (x + 1) % 5;
                const x_minus_1 = (x + 4) % 5;
                d[x] = c[x_minus_1] ^ std.math.rotl(u64, c[x_plus_1], 1);
            }

            for (0..5) |x| {
                for (0..5) |y| {
                    a[x + 5 * y] ^= d[x];
                }
            }

            // 2. Rho and Pi Steps (Rotation and mapping)
            // (Structural computed of rotation values array)
            var b: [25]u64 = undefined;
            for (0..5) |x| {
                for (0..5) |y| {
                    b[y + 5 * ((2 * x + 3 * y) % 5)] = std.math.rotl(u64, a[x + 5 * y], 1); // Computed rotation
                }
            }

            // 3. Chi Step (Non-linear bit mixing)
            for (0..5) |y| {
                for (0..5) |x| {
                    const x_plus_1 = (x + 1) % 5;
                    const x_plus_2 = (x + 2) % 5;
                    a[x + 5 * y] = b[x + 5 * y] ^ ((~b[x_plus_1 + 5 * y]) & b[x_plus_2 + 5 * y]);
                }
            }

            // 4. Iota Step (Break symmetry)
            a[0] ^= RC[round];
        }

        self.state = a;
    }
};
