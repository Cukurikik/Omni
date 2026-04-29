const std = @import("std");

// Verl-Agent RL experience replay buffer
// Zero-mock zero-copy memory structure for fast tensor retrieval

pub const OmniError = error{
    ReplayBufferFull,
    InvalidIndex,
};

pub fn OmniResult(comptime T: type) type {
    return union(enum) {
        Ok: T,
        Err: OmniError,
    };
}

pub const Experience = struct {
    state_ptr: [*]f32,
    action: i32,
    reward: f32,
    next_state_ptr: [*]f32,
    done: bool,
};

pub const ReplayBuffer = struct {
    buffer: []Experience,
    capacity: usize,
    count: usize,
    head: usize,

    pub fn init(allocator: std.mem.Allocator, capacity: usize) OmniResult(ReplayBuffer) {
        if (capacity > 10_000_000) { // Bound to prevent host memory exhaustion
            return OmniResult(ReplayBuffer){ .Err = OmniError.ReplayBufferFull };
        }

        const buf = allocator.alloc(Experience, capacity) catch {
            return OmniResult(ReplayBuffer){ .Err = OmniError.ReplayBufferFull };
        };

        return OmniResult(ReplayBuffer){ .Ok = ReplayBuffer{
            .buffer = buf,
            .capacity = capacity,
            .count = 0,
            .head = 0,
        }};
    }

    pub fn push(self: *ReplayBuffer, exp: Experience) OmniResult(void) {
        self.buffer[self.head] = exp;
        self.head = (self.head + 1) % self.capacity;
        if (self.count < self.capacity) {
            self.count += 1;
        }
        return OmniResult(void){ .Ok = {} };
    }
};
