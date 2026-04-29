// Omni LLM-Drop Pruner (Zig)
// System Layer: Zero-allocation transformer layer dropping execution logic.

const std = @import("std");

pub const PruneError = error{
    InvalidLayerCount,
    DropRateOutOfBounds,
};

pub fn calculate_active_layers(total_layers: u32, drop_rate: f32) PruneError!u32 {
    if (total_layers == 0) {
        return PruneError.InvalidLayerCount;
    }
    
    if (drop_rate < 0.0 or drop_rate >= 1.0) {
        return PruneError.DropRateOutOfBounds;
    }

    const drop_count: u32 = @intFromFloat(@as(f32, @floatFromInt(total_layers)) * drop_rate);
    return total_layers - drop_count;
}
