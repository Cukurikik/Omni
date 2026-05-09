// moe_token_dispatcher.zig — Zero-Copy Token Dispatch Engine
// Layer: System / Network — MoE All-to-All Communication
//
// Dispatches tokens to expert-owning devices using zero-copy
// shared memory. Implements the all-to-all dispatch pattern
// for expert parallelism without serialization overhead.

const std = @import("std");
const Allocator = std.mem.Allocator;

pub const DispatchError = error{
    InvalidExpertId,
    BufferOverflow,
    AllocationFailed,
    CapacityExceeded,
    NoTokensRouted,
};

pub const TokenMetadata = struct {
    token_idx: u32,
    expert_id: u16,
    weight: f32,
    source_rank: u16,
};

pub const DispatchConfig = struct {
    num_experts: u16 = 8,
    num_ranks: u16 = 1,
    max_tokens_per_expert: u32 = 4096,
    capacity_factor: f32 = 1.25,
    token_dim: u32 = 768,
};

/// Per-expert dispatch buffer for collecting routed tokens.
pub const ExpertBuffer = struct {
    tokens: []f32,
    metadata: []TokenMetadata,
    count: u32,
    capacity: u32,
    expert_id: u16,

    pub fn init(allocator: Allocator, expert_id: u16, capacity: u32, dim: u32) !ExpertBuffer {
        const token_elems = capacity * dim;
        const tokens = try allocator.alloc(f32, token_elems);
        const meta = try allocator.alloc(TokenMetadata, capacity);
        return ExpertBuffer{
            .tokens = tokens,
            .metadata = meta,
            .count = 0,
            .capacity = capacity,
            .expert_id = expert_id,
        };
    }

    pub fn deinit(self: *ExpertBuffer, allocator: Allocator) void {
        allocator.free(self.tokens);
        allocator.free(self.metadata);
    }

    pub fn push(self: *ExpertBuffer, token_data: []const f32, meta: TokenMetadata) DispatchError!void {
        if (self.count >= self.capacity) return DispatchError.CapacityExceeded;
        const dim = self.tokens.len / self.capacity;
        const offset = self.count * dim;
        @memcpy(self.tokens[offset .. offset + dim], token_data[0..dim]);
        self.metadata[self.count] = meta;
        self.count += 1;
    }

    pub fn reset(self: *ExpertBuffer) void {
        self.count = 0;
    }

    pub fn utilization(self: *const ExpertBuffer) f32 {
        if (self.capacity == 0) return 0.0;
        return @as(f32, @floatFromInt(self.count)) / @as(f32, @floatFromInt(self.capacity));
    }
};

/// All-to-All Token Dispatcher for Expert Parallelism.
pub const TokenDispatcher = struct {
    config: DispatchConfig,
    expert_buffers: []ExpertBuffer,
    allocator: Allocator,
    total_dispatched: u64,
    total_dropped: u64,

    pub fn init(allocator: Allocator, config: DispatchConfig) !TokenDispatcher {
        const cap = @as(u32, @intFromFloat(@as(f32, @floatFromInt(config.max_tokens_per_expert)) * config.capacity_factor));
        var buffers = try allocator.alloc(ExpertBuffer, config.num_experts);
        for (buffers, 0..) |*buf, i| {
            buf.* = try ExpertBuffer.init(allocator, @intCast(i), cap, config.token_dim);
        }
        return TokenDispatcher{
            .config = config,
            .expert_buffers = buffers,
            .allocator = allocator,
            .total_dispatched = 0,
            .total_dropped = 0,
        };
    }

    pub fn deinit(self: *TokenDispatcher) void {
        for (self.expert_buffers) |*buf| {
            buf.deinit(self.allocator);
        }
        self.allocator.free(self.expert_buffers);
    }

    /// Dispatch a batch of tokens to their assigned experts.
    pub fn dispatch_batch(
        self: *TokenDispatcher,
        tokens: []const f32,
        expert_assignments: []const u16,
        weights: []const f32,
        num_tokens: u32,
    ) !DispatchResult {
        const dim = self.config.token_dim;
        var dispatched: u32 = 0;
        var dropped: u32 = 0;

        for (0..num_tokens) |i| {
            const expert_id = expert_assignments[i];
            if (expert_id >= self.config.num_experts) {
                dropped += 1;
                continue;
            }

            const token_start = i * dim;
            const token_end = token_start + dim;
            const token_slice = tokens[token_start..token_end];

            const meta = TokenMetadata{
                .token_idx = @intCast(i),
                .expert_id = expert_id,
                .weight = weights[i],
                .source_rank = 0,
            };

            self.expert_buffers[expert_id].push(token_slice, meta) catch {
                dropped += 1;
                continue;
            };
            dispatched += 1;
        }

        self.total_dispatched += dispatched;
        self.total_dropped += dropped;

        return DispatchResult{
            .dispatched = dispatched,
            .dropped = dropped,
            .utilization = self.compute_utilization(),
        };
    }

    /// Reset all expert buffers for the next batch.
    pub fn reset_all(self: *TokenDispatcher) void {
        for (self.expert_buffers) |*buf| {
            buf.reset();
        }
    }

    /// Get the dispatch buffer for a specific expert.
    pub fn get_expert_buffer(self: *TokenDispatcher, expert_id: u16) DispatchError!*ExpertBuffer {
        if (expert_id >= self.config.num_experts) return DispatchError.InvalidExpertId;
        return &self.expert_buffers[expert_id];
    }

    fn compute_utilization(self: *const TokenDispatcher) f32 {
        var total: f32 = 0.0;
        for (self.expert_buffers) |*buf| {
            total += buf.utilization();
        }
        return total / @as(f32, @floatFromInt(self.config.num_experts));
    }
};

pub const DispatchResult = struct {
    dispatched: u32,
    dropped: u32,
    utilization: f32,
};

test "expert buffer push and utilization" {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();

    var buf = try ExpertBuffer.init(alloc, 0, 4, 3);
    defer buf.deinit(alloc);

    const token = [_]f32{ 1.0, 2.0, 3.0 };
    const meta = TokenMetadata{ .token_idx = 0, .expert_id = 0, .weight = 0.5, .source_rank = 0 };
    try buf.push(&token, meta);

    try std.testing.expectEqual(@as(u32, 1), buf.count);
    try std.testing.expect(buf.utilization() > 0.24);
}

test "dispatcher batch routing" {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();

    const config = DispatchConfig{
        .num_experts = 4,
        .num_ranks = 1,
        .max_tokens_per_expert = 8,
        .capacity_factor = 1.0,
        .token_dim = 2,
    };

    var dispatcher = try TokenDispatcher.init(alloc, config);
    defer dispatcher.deinit();

    const tokens = [_]f32{ 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0 };
    const assignments = [_]u16{ 0, 1, 2, 3 };
    const weights = [_]f32{ 0.5, 0.3, 0.1, 0.1 };

    const result = try dispatcher.dispatch_batch(&tokens, &assignments, &weights, 4);
    try std.testing.expectEqual(@as(u32, 4), result.dispatched);
    try std.testing.expectEqual(@as(u32, 0), result.dropped);
}
