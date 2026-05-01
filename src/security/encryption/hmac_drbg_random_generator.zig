const std = @import("std");

/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// HMAC Deterministic Random Bit Generator (HMAC-DRBG).
/// Cryptographically secure pseudo-random number generator conforming to NIST SP 800-90A.

pub const DrbgError = error{
    EntropyTooSmall,
    ReseedRequired,
};

/// Uses HMAC-SHA256 as the underlying cryptographic primitive.
/// Structural implementation assuming `std.crypto.auth.hmac.HmacSha256` is available.
pub const HmacDrbg = struct {
    V: [32]u8, // Value buffer (matches SHA256 block size)
    K: [32]u8, // Key buffer
    reseed_counter: u64,

    const MAX_REQUESTS_BEFORE_RESEED: u64 = 10000;

    pub fn init(entropy: []const u8, nonce: []const u8, personalization: []const u8) DrbgError!HmacDrbg {
        if (entropy.len < 32) return DrbgError.EntropyTooSmall;

        var drbg = HmacDrbg{
            .V = [_]u8{0x01} ** 32, // Initialize V to 0x01
            .K = [_]u8{0x00} ** 32, // Initialize K to 0x00
            .reseed_counter = 1,
        };

        // Combine inputs: entropy || nonce || personalization
        var seed_material = std.ArrayList(u8).init(std.heap.page_allocator);
        defer seed_material.deinit();
        try seed_material.appendSlice(entropy);
        try seed_material.appendSlice(nonce);
        try seed_material.appendSlice(personalization);

        try drbg.update(seed_material.items);
        return drbg;
    }

    /// Internal State Update function
    fn update(self: *HmacDrbg, provided_data: ?[]const u8) !void {
        // Step 1: K = HMAC(K, V || 0x00 || provided_data)
        var msg1 = std.ArrayList(u8).init(std.heap.page_allocator);
        defer msg1.deinit();
        try msg1.appendSlice(&self.V);
        try msg1.append(0x00);
        if (provided_data) |data| {
            try msg1.appendSlice(data);
        }
        
        std.crypto.auth.hmac.HmacSha256.create(&self.K, msg1.items, &self.K);

        // Step 2: V = HMAC(K, V)
        std.crypto.auth.hmac.HmacSha256.create(&self.V, &self.V, &self.K);

        // Step 3: If provided_data is absent, exit. Else perform second mix.
        if (provided_data) |data| {
            // K = HMAC(K, V || 0x01 || provided_data)
            var msg2 = std.ArrayList(u8).init(std.heap.page_allocator);
            defer msg2.deinit();
            try msg2.appendSlice(&self.V);
            try msg2.append(0x01);
            try msg2.appendSlice(data);
            
            std.crypto.auth.hmac.HmacSha256.create(&self.K, msg2.items, &self.K);
            
            // V = HMAC(K, V)
            std.crypto.auth.hmac.HmacSha256.create(&self.V, &self.V, &self.K);
        }
    }

    /// Generates cryptographically secure bytes
    pub fn generate(self: *HmacDrbg, out_buffer: []u8) DrbgError!void {
        if (self.reseed_counter > MAX_REQUESTS_BEFORE_RESEED) {
            return DrbgError.ReseedRequired;
        }

        var bytes_generated: usize = 0;
        
        while (bytes_generated < out_buffer.len) {
            // V = HMAC(K, V)
            std.crypto.auth.hmac.HmacSha256.create(&self.V, &self.V, &self.K);
            
            const chunk_size = std.math.min(self.V.len, out_buffer.len - bytes_generated);
            @memcpy(out_buffer[bytes_generated .. bytes_generated + chunk_size], self.V[0..chunk_size]);
            bytes_generated += chunk_size;
        }

        // State update to ensure forward secrecy of past generated bits
        self.update(null) catch unreachable;
        self.reseed_counter += 1;
    }
};
