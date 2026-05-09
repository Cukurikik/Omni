// omni_llm_perplexity.rs — Language Model Perplexity Scorer
// Layer: Domain / Analytics
// Inspired by: Furyton/awesome-language-model-analysis
//
// Calculates the Perplexity of a language model over a dataset based on
// its next-token cross-entropy probabilities. Useful for evaluating model
// degradation during fine-tuning or quantization. Zero mock.

pub struct OmniPerplexityScorer;

impl OmniPerplexityScorer {
    /// Computes perplexity from a sequence of Cross-Entropy losses.
    /// Formula: Perplexity = exp(1/N * sum(L_i))
    ///
    /// # Arguments
    /// * `token_losses` - A slice of cross-entropy losses for each token in a sequence.
    ///
    /// # Returns
    /// * `f64` - The calculated perplexity.
    pub fn compute_from_losses(token_losses: &[f64]) -> f64 {
        if token_losses.is_empty() {
            return f64::INFINITY;
        }

        let sum_loss: f64 = token_losses.iter().sum();
        let avg_loss = sum_loss / (token_losses.len() as f64);
        
        avg_loss.exp()
    }

    /// Computes perplexity directly from predicted probabilities.
    /// 
    /// # Arguments
    /// * `target_probs` - A slice of probabilities assigned to the actual target tokens.
    pub fn compute_from_probabilities(target_probs: &[f64]) -> f64 {
        if target_probs.is_empty() {
            return f64::INFINITY;
        }

        let mut sum_log_prob = 0.0;
        for &prob in target_probs {
            // Prevent log(0)
            let p = if prob < 1e-12 { 1e-12 } else { prob };
            sum_log_prob += p.ln();
        }

        let avg_neg_log_prob = -(sum_log_prob / (target_probs.len() as f64));
        
        avg_neg_log_prob.exp()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_perfect_model() {
        let probs = vec![1.0, 1.0, 1.0];
        let ppl = OmniPerplexityScorer::compute_from_probabilities(&probs);
        assert!((ppl - 1.0).abs() < 1e-6); // Perfect model has perplexity of 1.0
    }
}
