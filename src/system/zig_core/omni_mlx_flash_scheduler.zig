// Omni MLX Flash Layer Scheduler (Zig)
// Ref: matt-k-wong/mlx-flash
const std = @import("std");
pub fn computeLayersInRAM(total_layers: u32, ram_gb: f64, layer_size_mb: f64) u32 {
    const avail = ram_gb * 1024.0;
    const fits: u32 = @intFromFloat(avail / @max(layer_size_mb, 0.01));
    return if (fits < total_layers) fits else total_layers;
}
pub fn streamRatio(total_layers: u32, in_ram: u32) f64 {
    return @as(f64, @floatFromInt(total_layers - in_ram)) / @as(f64, @floatFromInt(@max(total_layers, 1)));
}
