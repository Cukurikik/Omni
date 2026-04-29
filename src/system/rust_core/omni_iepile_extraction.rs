// Omni IEPile Entity Extraction Kernel (Rust)
// Ref: zjunlp/IEPile — ACL 2024

#[derive(Debug, Clone)]
pub struct Entity { pub text: String, pub entity_type: String, pub start: usize, pub end: usize }

pub fn extract_entities_by_pattern(text: &str, patterns: &[(&str, &str)]) -> Vec<Entity> {
    let mut entities = Vec::new();
    let text_lower = text.to_lowercase();
    for (pattern, etype) in patterns {
        let pat_lower = pattern.to_lowercase();
        let mut start = 0;
        while let Some(pos) = text_lower[start..].find(&pat_lower) {
            let abs_pos = start + pos;
            entities.push(Entity {
                text: text[abs_pos..abs_pos + pattern.len()].to_string(),
                entity_type: etype.to_string(), start: abs_pos, end: abs_pos + pattern.len(),
            });
            start = abs_pos + 1;
        }
    }
    entities
}

pub fn ie_f1(tp: usize, fp: usize, fn_count: usize) -> (f64, f64, f64) {
    let precision = tp as f64 / (tp + fp).max(1) as f64;
    let recall = tp as f64 / (tp + fn_count).max(1) as f64;
    let f1 = if precision + recall > 0.0 { 2.0 * precision * recall / (precision + recall) } else { 0.0 };
    (precision, recall, f1)
}
