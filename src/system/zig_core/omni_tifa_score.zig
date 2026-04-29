// Omni TIFA VQA Score (Zig)
// Ref: Yushi-Hu/tifa — Apache-2.0
const std = @import("std");
pub fn computeTifaScore(correct: []const bool) f64 {
    if (correct.len == 0) return 0;
    var n_correct: usize = 0;
    for (correct) |c| { if (c) n_correct += 1; }
    return @as(f64, @floatFromInt(n_correct)) / @as(f64, @floatFromInt(correct.len));
}
pub fn elementWiseBreakdown(types: []const u8, correct: []const bool, n_types: usize) [8]f64 {
    var counts = [_]f64{0} ** 8;
    var totals = [_]f64{0} ** 8;
    for (types, 0..) |t, i| {
        if (t < 8 and i < correct.len) {
            totals[t] += 1;
            if (correct[i]) counts[t] += 1;
        }
    }
    var result = [_]f64{0} ** 8;
    for (0..8) |k| result[k] = if (totals[k] > 0) counts[k] / totals[k] else 0;
    return result;
}
