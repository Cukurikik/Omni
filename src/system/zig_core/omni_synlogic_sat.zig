// Omni SynLogic SAT Solver (Zig)
// Ref: MiniMax-AI/SynLogic — MIT
const std = @import("std");
pub fn check_clause(clause: []const i32, assignment: []const bool) bool {
    for (clause) |lit| {
        const v: usize = @intCast(if (lit > 0) lit - 1 else -lit - 1);
        if (v >= assignment.len) continue;
        const val = assignment[v];
        if ((lit > 0 and val) or (lit < 0 and !val)) return true;
    }
    return false;
}
pub fn check_sat(clauses: []const []const i32, assignment: []const bool) bool {
    for (clauses) |clause| { if (!check_clause(clause, assignment)) return false; }
    return true;
}
