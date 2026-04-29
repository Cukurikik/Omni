// Omni ToolEmu Safety Gateway (Rust)
// Ref: ryoungj/ToolEmu — Apache-2.0
pub fn assess_risk(action: &str, args: &[&str]) -> (f64, Vec<String>) {
    let mut score = 0.0f64; let mut flags = Vec::new();
    let dangerous = [("delete", 0.9), ("write", 0.6), ("execute", 0.8), ("send", 0.5)];
    let action_l = action.to_lowercase();
    for (da, w) in &dangerous {
        if action_l.contains(da) { score = score.max(*w); flags.push(format!("action_{}", da)); }
    }
    let sensitive = ["password", "token", "key", "secret"];
    for arg in args {
        let a = arg.to_lowercase();
        for s in &sensitive { if a.contains(s) { score = (score + 0.3).min(1.0); flags.push(format!("sensitive_{}", s)); } }
    }
    (score, flags)
}
