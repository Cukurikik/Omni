/// LLM-Pruner — Structural Pruning via Weight Magnitude
/// Taylor importance scoring for group pruning

pub struct OmniResult<T, E> { pub value: Option<T>, pub error: Option<E> }

pub struct PruningMask { pub indices: Vec<usize>, pub pruned_ratio: f32 }

pub fn compute_taylor_importance(weights: &[f32], grads: &[f32]) -> OmniResult<Vec<f32>, String> {
    if weights.len() != grads.len() { return OmniResult { value: None, error: Some("W/G length mismatch".into()) }; }
    if weights.is_empty() { return OmniResult { value: None, error: Some("Empty weights".into()) }; }
    if weights.len() > 100_000_000 { return OmniResult { value: None, error: Some("Exceeds 100M params".into()) }; }
    let scores: Vec<f32> = weights.iter().zip(grads.iter())
        .map(|(w, g)| (w * g).abs())
        .collect();
    OmniResult { value: Some(scores), error: None }
}

pub fn generate_pruning_mask(scores: &[f32], ratio: f32) -> OmniResult<PruningMask, String> {
    if ratio <= 0.0 || ratio >= 1.0 { return OmniResult { value: None, error: Some("Ratio must be in (0,1)".into()) }; }
    let mut indexed: Vec<(usize, f32)> = scores.iter().cloned().enumerate().collect();
    indexed.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap());
    let prune_count = (scores.len() as f32 * ratio) as usize;
    let indices: Vec<usize> = indexed[..prune_count].iter().map(|(i, _)| *i).collect();
    OmniResult { value: Some(PruningMask { indices, pruned_ratio: ratio }), error: None }
}
