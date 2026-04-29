// SPIN Self-Play Token Sampler
// Ownership-safe sampler for iterative self-play fine-tuning

pub struct OmniResult<T, E> { pub value: Option<T>, pub error: Option<E> }

pub struct SampledToken { pub token_id: u32, pub log_prob: f64 }

pub struct SelfPlaySampler {
    temperature: f64,
    top_p: f64,
    max_new_tokens: u32,
}

impl SelfPlaySampler {
    pub fn new(temp: f64, top_p: f64, max_tokens: u32) -> OmniResult<Self, String> {
        if temp <= 0.0 || temp > 5.0 {
            return OmniResult { value: None, error: Some("Temperature must be in (0, 5]".into()) };
        }
        if top_p <= 0.0 || top_p > 1.0 {
            return OmniResult { value: None, error: Some("top_p must be in (0, 1]".into()) };
        }
        if max_tokens > 16384 {
            return OmniResult { value: None, error: Some("Max tokens exceeds 16384 limit".into()) };
        }
        OmniResult { value: Some(Self { temperature: temp, top_p, max_new_tokens: max_tokens }), error: None }
    }

    pub fn sample_nucleus(&self, logits: &[f64]) -> OmniResult<SampledToken, String> {
        if logits.is_empty() || logits.len() > 256000 {
            return OmniResult { value: None, error: Some("Vocab size out of bounds".into()) };
        }
        // Apply temperature scaling
        let max_logit = logits.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
        let scaled: Vec<f64> = logits.iter().map(|l| ((l - max_logit) / self.temperature).exp()).collect();
        let sum: f64 = scaled.iter().sum();
        if sum <= 0.0 {
            return OmniResult { value: None, error: Some("Softmax sum is zero".into()) };
        }
        let probs: Vec<f64> = scaled.iter().map(|s| s / sum).collect();

        // Nucleus (top-p) sampling: sort by probability descending
        let mut indexed: Vec<(usize, f64)> = probs.iter().cloned().enumerate().collect();
        indexed.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
        let mut cumulative = 0.0;
        for (idx, prob) in &indexed {
            cumulative += prob;
            if cumulative >= self.top_p {
                let log_prob = prob.ln();
                return OmniResult { value: Some(SampledToken { token_id: *idx as u32, log_prob }), error: None };
            }
        }
        let (idx, prob) = indexed[0];
        OmniResult { value: Some(SampledToken { token_id: idx as u32, log_prob: prob.ln() }), error: None }
    }
}
