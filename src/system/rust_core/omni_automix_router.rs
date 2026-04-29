// Omni AutoMix LLM Router (Rust)
// Ref: automix-llm/automix
pub struct RouterConfig { pub threshold: f64, pub cost_small: f64, pub cost_large: f64 }
pub fn self_verify(answer_tokens: &[u64], context_tokens: &[u64]) -> f64 {
    if answer_tokens.is_empty() { return 0.0; }
    let ctx: std::collections::HashSet<_> = context_tokens.iter().collect();
    let overlap = answer_tokens.iter().filter(|t| ctx.contains(t)).count();
    overlap as f64 / answer_tokens.len() as f64
}
pub fn route(sv_score: f64, config: &RouterConfig) -> &'static str {
    if sv_score >= config.threshold { "small" } else { "large" }
}
