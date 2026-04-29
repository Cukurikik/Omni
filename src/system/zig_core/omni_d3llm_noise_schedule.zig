// Omni d3LLM Noise Schedule Hash (Zig)
// System: Deterministic noise scheduling for diffusion LLM.
// Ref: hao-ai-lab/d3LLM
const std = @import("std");
pub fn noise_level(step: u32, total_steps: u32) -> f32 {
    if (total_steps == 0) return 0.0;
    return 1.0 - @as(f32, @floatFromInt(step)) / @as(f32, @floatFromInt(total_steps));
}
pub fn cosine_schedule(step: u32, total_steps: u32) -> f32 {
    if (total_steps == 0) return 0.0;
    const pi: f32 = 3.14159265;
    return 0.5 * (1.0 + @cos(pi * @as(f32, @floatFromInt(step)) / @as(f32, @floatFromInt(total_steps))));
}
