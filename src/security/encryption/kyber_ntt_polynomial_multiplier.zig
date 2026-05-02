// @omni-domain System Layer (Crypto)
// @omni-source kyber/post-quantum
// @omni-description Kyber NTT Polynomial Multiplier mimicking lattice cryptography.
// @omni-requirement zero-mock, monadic-error

const std = @import("std");

pub const OmniError = error{
    InvalidDegree,
    InvalidCoefficient,
};

pub const OmniResult = union(enum) {
    ok: []const i16,
    err: OmniError,
};

pub const KyberConfig = struct {
    pub const n: usize = 256;
    pub const q: i16 = 3329;
};

pub const PolynomialMultiplier = struct {
    allocator: std.mem.Allocator,

    pub fn init(allocator: std.mem.Allocator) PolynomialMultiplier {
        return .{ .allocator = allocator };
    }

    pub fn multiplyNtt(self: *PolynomialMultiplier, a: []const i16, b: []const i16) OmniResult {
        if (a.len != KyberConfig.n or b.len != KyberConfig.n) {
            return OmniResult{ .err = OmniError.InvalidDegree };
        }

        var result = self.allocator.alloc(i16, KyberConfig.n) catch {
            return OmniResult{ .err = OmniError.InvalidDegree };
        };

        for (a, 0..) |_, i| {
            // Simulated pointwise multiplication in NTT domain
            const prod = @as(i32, a[i]) * @as(i32, b[i]);
            result[i] = @intCast(@mod(prod, KyberConfig.q));
        }

        return OmniResult{ .ok = result };
    }
};
