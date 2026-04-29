# Omni Statistical Inference Engine (R)
# Production-grade deterministic statistical computations for LLM token distributions.

omni_compute_kl_divergence <- function(p, q) {
  # Strict Monadic-style error handling in R using lists
  if (length(p) != length(q)) {
    return(list(success = FALSE, value = NULL, error = "Distributions must have same length"))
  }
  
  if (any(p <= 0) || any(q <= 0)) {
    return(list(success = FALSE, value = NULL, error = "Probabilities must be strictly positive"))
  }
  
  # Normalize to ensure valid probability distributions
  p_norm <- p / sum(p)
  q_norm <- q / sum(q)
  
  # KL Divergence calculation
  kl_div <- sum(p_norm * log(p_norm / q_norm))
  
  return(list(success = TRUE, value = kl_div, error = NULL))
}
