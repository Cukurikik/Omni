// Omni Lion KL Divergence Kernel (Zig)
// Ref: YJiangcm/Lion — EMNLP 2023
const std = @import("std");
const math = std.math;

pub fn kl_divergence(p: []const f64, q: []const f64) f64 {
    var kl: f64 = 0;
    const n = @min(p.len, q.len);
    for (0..n) |i| {
        if (p[i] > 1e-12 and q[i] > 1e-12) {
            kl += p[i] * @log(p[i] / q[i]);
        }
    }
    return kl;
}

pub fn softmax(logits: []const f64, out: []f64) void {
    var max_val: f64 = -1e30;
    for (logits) |l| { if (l > max_val) max_val = l; }
    var sum: f64 = 0;
    for (logits, 0..) |l, i| {
        out[i] = @exp(l - max_val);
        sum += out[i];
    }
    for (out[0..logits.len]) |*o| { o.* /= @max(sum, 1e-12); }
}

pub fn distillation_loss(student_logits: []const f64, teacher_logits: []const f64,
                          temperature: f64) f64 {
    var s_prob: [512]f64 = undefined;
    var t_prob: [512]f64 = undefined;
    const n = @min(student_logits.len, 512);
    var s_scaled: [512]f64 = undefined;
    var t_scaled: [512]f64 = undefined;
    for (0..n) |i| { s_scaled[i] = student_logits[i] / temperature; t_scaled[i] = teacher_logits[i] / temperature; }
    softmax(s_scaled[0..n], s_prob[0..n]);
    softmax(t_scaled[0..n], t_prob[0..n]);
    return kl_divergence(t_prob[0..n], s_prob[0..n]) * temperature * temperature;
}
