// ===========================================================================
// OMNI SYSTEM LAYER — TLS PROTOCOL FUZZER ENGINE
// ===========================================================================
// Source Paradigm : tlsfuzzer/tlsfuzzer (runner.py, ConnectionState)
// Domain Layer   : System (Memory-safe protocol-level testing)
// Language        : Zig
// Function        : State-machine TLS handshake fuzzer that generates
//                   malformed ClientHello/record-layer payloads, walks a
//                   conversation decision tree, and validates server responses
// ===========================================================================

const std = @import("std");

// ---- TLS Constants --------------------------------------------------------

pub const ContentType = enum(u8) {
    change_cipher_spec = 20,
    alert = 21,
    handshake = 22,
    application_data = 23,
};

pub const HandshakeType = enum(u8) {
    client_hello = 1,
    server_hello = 2,
    certificate = 11,
    server_key_exchange = 12,
    certificate_request = 13,
    server_hello_done = 14,
    certificate_verify = 15,
    client_key_exchange = 16,
    finished = 20,
};

pub const AlertLevel = enum(u8) {
    warning = 1,
    fatal = 2,
};

pub const AlertDescription = enum(u8) {
    close_notify = 0,
    unexpected_message = 10,
    bad_record_mac = 20,
    handshake_failure = 40,
    protocol_version = 70,
    insufficient_security = 71,
    internal_error = 80,
};

pub const TlsVersion = struct {
    major: u8,
    minor: u8,

    pub fn tls12() TlsVersion {
        return .{ .major = 3, .minor = 3 };
    }
    pub fn tls13() TlsVersion {
        return .{ .major = 3, .minor = 4 };
    }
};

// ---- Connection State (mirrors tlsfuzzer/runner.py ConnectionState) --------

pub const ConnectionState = struct {
    client_version: TlsVersion,
    server_version: TlsVersion,
    cipher_suite: u16,
    client_random: [32]u8,
    server_random: [32]u8,
    session_id: [32]u8,
    session_id_len: u8,
    handshake_hash: [64]u8,
    hash_len: usize,
    is_resumed: bool,
    extended_master_secret: bool,
    encrypt_then_mac: bool,
    messages_sent: u32,
    messages_received: u32,

    pub fn init() ConnectionState {
        return ConnectionState{
            .client_version = TlsVersion.tls12(),
            .server_version = TlsVersion.tls12(),
            .cipher_suite = 0,
            .client_random = std.mem.zeroes([32]u8),
            .server_random = std.mem.zeroes([32]u8),
            .session_id = std.mem.zeroes([32]u8),
            .session_id_len = 0,
            .handshake_hash = std.mem.zeroes([64]u8),
            .hash_len = 0,
            .is_resumed = false,
            .extended_master_secret = false,
            .encrypt_then_mac = false,
            .messages_sent = 0,
            .messages_received = 0,
        };
    }
};

// ---- Record Layer ---------------------------------------------------------

pub const TlsRecord = struct {
    content_type: ContentType,
    version: TlsVersion,
    length: u16,
    payload: [16384]u8,
    payload_len: u16,

    /// Build a well-formed TLS record from raw bytes.
    pub fn fromPayload(ct: ContentType, ver: TlsVersion, data: []const u8) TlsRecord {
        var rec = TlsRecord{
            .content_type = ct,
            .version = ver,
            .length = @intCast(data.len),
            .payload = std.mem.zeroes([16384]u8),
            .payload_len = @intCast(data.len),
        };
        @memcpy(rec.payload[0..data.len], data);
        return rec;
    }

    /// Build a MALFORMED record with incorrect length for fuzzing.
    pub fn malformedLength(ct: ContentType, ver: TlsVersion, data: []const u8, fake_len: u16) TlsRecord {
        var rec = fromPayload(ct, ver, data);
        rec.length = fake_len; // length mismatch = fuzz vector
        return rec;
    }
};

// ---- Fuzz Payloads --------------------------------------------------------

/// Generate a minimal ClientHello payload for TLS 1.2.
pub fn buildClientHello(state: *ConnectionState, allocator: std.mem.Allocator) ![]u8 {
    _ = allocator;
    var buf: [512]u8 = std.mem.zeroes([512]u8);
    var pos: usize = 0;

    // Handshake type: ClientHello (1)
    buf[pos] = @intFromEnum(HandshakeType.client_hello);
    pos += 1;

    // Length placeholder (3 bytes) — will backpatch
    const len_pos = pos;
    pos += 3;

    // Client version
    buf[pos] = state.client_version.major;
    pos += 1;
    buf[pos] = state.client_version.minor;
    pos += 1;

    // Client random (32 bytes) — fill with deterministic pattern for fuzz
    for (0..32) |i| {
        state.client_random[i] = @intCast(i ^ 0xAB);
        buf[pos] = state.client_random[i];
        pos += 1;
    }

    // Session ID length = 0
    buf[pos] = 0;
    pos += 1;

    // Cipher suites: TLS_RSA_WITH_AES_128_CBC_SHA (0x002F)
    buf[pos] = 0;
    pos += 1;
    buf[pos] = 2; // 2 bytes of cipher suites
    pos += 1;
    buf[pos] = 0x00;
    pos += 1;
    buf[pos] = 0x2F;
    pos += 1;

    // Compression methods: null (0)
    buf[pos] = 1; // 1 method
    pos += 1;
    buf[pos] = 0; // null compression
    pos += 1;

    // Backpatch handshake length
    const body_len = pos - len_pos - 3;
    buf[len_pos] = 0;
    buf[len_pos + 1] = @intCast((body_len >> 8) & 0xFF);
    buf[len_pos + 2] = @intCast(body_len & 0xFF);

    state.messages_sent += 1;

    // Return a stack copy (caller must copy if needed)
    var result: [512]u8 = undefined;
    @memcpy(&result, &buf);
    return result[0..pos];
}

/// Guess the TLS response type from raw record data (mirrors runner.py guess_response).
pub fn guessResponse(ct: ContentType, data: []const u8) []const u8 {
    return switch (ct) {
        .change_cipher_spec => "ChangeCipherSpec",
        .alert => if (data.len >= 2) "Alert" else "Alert(invalid)",
        .handshake => if (data.len > 0) "Handshake" else "Handshake(empty)",
        .application_data => "ApplicationData",
    };
}

// ---- Conversation Runner (mirrors Runner.run()) ---------------------------

pub const FuzzVerdict = enum {
    pass,
    fail_unexpected_response,
    fail_timeout,
    fail_connection_reset,
};

/// Run a single fuzz scenario: send a crafted payload, check expected response.
pub fn runFuzzScenario(
    state: *ConnectionState,
    send_payload: []const u8,
    expected_ct: ContentType,
) FuzzVerdict {
    _ = send_payload;

    // In production: open TCP socket, send record, read response
    // Here we model the decision-tree logic from runner.py

    state.messages_sent += 1;

    // Simulate server response (production: actual recv)
    const simulated_response_ct = ContentType.alert;
    state.messages_received += 1;

    if (simulated_response_ct == expected_ct) {
        return .pass;
    } else {
        return .fail_unexpected_response;
    }
}

// pub fn main() !void {
//     var state = ConnectionState.init();
//     var gpa = std.heap.GeneralPurposeAllocator(.{}){};
//     const hello = try buildClientHello(&state, gpa.allocator());
//     const record = TlsRecord.fromPayload(.handshake, TlsVersion.tls12(), hello);
//     const verdict = runFuzzScenario(&state, hello, .handshake);
//     std.debug.print("Verdict: {}\n", .{verdict});
// }
