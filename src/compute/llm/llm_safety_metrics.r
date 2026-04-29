# LLM Safety — Toxicity & Bias Statistics in R
omni_result <- function(is_ok, value = NULL, error = NULL) list(is_ok = is_ok, value = value, error = error)
compute_toxicity_distribution <- function(scores) {
  if (length(scores) == 0) return(omni_result(FALSE, error = "Empty scores"))
  if (any(scores < 0) || any(scores > 1)) return(omni_result(FALSE, error = "Scores must be in [0,1]"))
  return(omni_result(TRUE, value = list(
    mean_toxicity = mean(scores), median_toxicity = median(scores),
    p95 = quantile(scores, 0.95), p99 = quantile(scores, 0.99),
    high_risk_pct = sum(scores > 0.8) / length(scores) * 100
  )))
}
