// @omni-layer System | @omni-source lucidrains/coconut-pytorch
// @omni-description Continuous thought token allocator in Zig: zero-copy latent state
// memory management for chain-of-continuous-thought inference.
// @omni-lang Zig | @omni-batch 16 | @omni-semester 16

const std = @import("std");

pub const ThoughtError = error{
    OutOfMemory,
    InvalidDimension,
    EmptyInput,
};

pub const ThoughtToken = struct {
    data: []f32,
    thought_idx: u32,
    depth: u32,
    score: f64,
};

pub const ThoughtPool = struct {
    allocator: std.mem.Allocator,
    tokens: std.ArrayList(ThoughtToken),
    d_model: u32,
    max_thoughts: u32,
    active_count: u32,

    pub fn init(allocator: std.mem.Allocator, d_model: u32, max_thoughts: u32) ThoughtPool {
        return .{
            .allocator = allocator,
            .tokens = std.ArrayList(ThoughtToken).init(allocator),
            .d_model = d_model,
            .max_thoughts = max_thoughts,
            .active_count = 0,
        };
    }

    pub fn deinit(self: *ThoughtPool) void {
        for (self.tokens.items) |token| {
            self.allocator.free(token.data);
        }
        self.tokens.deinit();
    }

    pub fn allocate_thought(self: *ThoughtPool, depth: u32) !*ThoughtToken {
        if (self.active_count >= self.max_thoughts) return ThoughtError.OutOfMemory;
        const data = try self.allocator.alloc(f32, self.d_model);
        @memset(data, 0);
        const token = ThoughtToken{
            .data = data,
            .thought_idx = self.active_count,
            .depth = depth,
            .score = 0.0,
        };
        try self.tokens.append(token);
        self.active_count += 1;
        return &self.tokens.items[self.tokens.items.len - 1];
    }

    pub fn compute_thought_norm(self: *const ThoughtPool, idx: u32) f64 {
        if (idx >= self.tokens.items.len) return 0.0;
        const data = self.tokens.items[idx].data;
        var sum: f64 = 0.0;
        for (data) |v| { sum += @as(f64, v) * @as(f64, v); }
        return @sqrt(sum);
    }

    pub fn get_best_thought(self: *const ThoughtPool) ?*const ThoughtToken {
        if (self.tokens.items.len == 0) return null;
        var best_idx: usize = 0;
        var best_score: f64 = self.tokens.items[0].score;
        for (self.tokens.items, 0..) |token, i| {
            if (token.score > best_score) {
                best_score = token.score;
                best_idx = i;
            }
        }
        return &self.tokens.items[best_idx];
    }
};
