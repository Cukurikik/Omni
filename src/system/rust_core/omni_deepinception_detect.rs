// Omni DeepInception Pattern Detector (Rust)
// Ref: tmlr-group/DeepInception — MIT
pub fn detect_nesting_depth(text: &str) -> usize {
    let markers = ["layer", "scene", "level", "step", "imagine", "pretend"];
    markers.iter().filter(|m| text.to_lowercase().contains(*m)).count()
}
pub fn inception_risk_score(text: &str) -> f64 {
    let inception = ["create a story","imagine a world","roleplay as","pretend you are","nested scenario"];
    let harmful = ["violence","weapon","hack","exploit","steal","attack","malware"];
    let tl = text.to_lowercase();
    let im = inception.iter().filter(|m| tl.contains(*m)).count() as f64;
    let hm = harmful.iter().filter(|m| tl.contains(*m)).count() as f64;
    (im * 0.15 + hm * 0.2 + detect_nesting_depth(text) as f64 * 0.1).min(1.0)
}
