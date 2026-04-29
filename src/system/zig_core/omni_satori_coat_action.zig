// Omni Satori COAT Action Hash (Zig)
// Ref: satori-reasoning/Satori — ICML'25
pub const Action = enum(u8) { continue_act = 0, reflect = 1, explore = 2 };
pub fn select_action(confidence: f32, step: u32, max_steps: u32) -> Action {
    if (confidence < 0.2 and step > max_steps / 2) return .explore;
    if (confidence < 0.4) return .reflect;
    return .continue_act;
}
pub fn coat_reward(correct: bool, n_steps: u32, max_steps: u32) -> f32 {
    const base: f32 = if (correct) 1.0 else -0.5;
    const eff: f32 = 0.1 * (1.0 - @as(f32, @floatFromInt(n_steps)) / @as(f32, @floatFromInt(max_steps)));
    return base + eff;
}
