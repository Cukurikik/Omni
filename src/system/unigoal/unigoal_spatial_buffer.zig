const std = @import("std");

// UniGoal zero-shot goal-oriented navigation spatial buffer
// Pre-allocates hardware-bounded spatial memory for pathfinding

pub const OmniError = error{
    SpatialBufferExhausted,
    InvalidCoordinate,
};

pub fn OmniResult(comptime T: type) type {
    return union(enum) {
        Ok: T,
        Err: OmniError,
    };
}

pub const SpatialBuffer = struct {
    grid: []u8,
    width: usize,
    height: usize,
    max_cells: usize,

    pub fn init(width: usize, height: usize) OmniResult(SpatialBuffer) {
        const max_cells = 1000 * 1000; // 1 Million cells bound
        if (width * height > max_cells) {
            return OmniResult(SpatialBuffer){ .Err = OmniError.SpatialBufferExhausted };
        }

        const raw_grid = std.heap.page_allocator.alloc(u8, width * height) catch {
            return OmniResult(SpatialBuffer){ .Err = OmniError.SpatialBufferExhausted };
        };

        return OmniResult(SpatialBuffer){ .Ok = SpatialBuffer{
            .grid = raw_grid,
            .width = width,
            .height = height,
            .max_cells = max_cells,
        }};
    }

    pub fn update_cell(self: *SpatialBuffer, x: usize, y: usize, state: u8) OmniResult(void) {
        if (x >= self.width or y >= self.height) {
            return OmniResult(void){ .Err = OmniError.InvalidCoordinate };
        }
        
        self.grid[y * self.width + x] = state;
        return OmniResult(void){ .Ok = {} };
    }
};
