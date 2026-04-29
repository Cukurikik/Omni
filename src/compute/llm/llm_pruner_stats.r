# LLM-Pruner — Pruning Statistics in R
omni_result <- function(is_ok, value = NULL, error = NULL) {
  list(is_ok = is_ok, value = value, error = error)
}
compute_sparsity <- function(weights) {
  if (length(weights) == 0) return(omni_result(FALSE, error = "Empty weights"))
  if (length(weights) > 100000000) return(omni_result(FALSE, error = "Exceeds 100M params"))
  zeros <- sum(weights == 0)
  sparsity <- zeros / length(weights)
  return(omni_result(TRUE, value = list(sparsity = sparsity, zero_count = zeros, total = length(weights))))
}
compute_pruning_impact <- function(original_perplexity, pruned_perplexity) {
  if (original_perplexity <= 0 || pruned_perplexity <= 0) return(omni_result(FALSE, error = "Perplexity must be positive"))
  degradation <- (pruned_perplexity - original_perplexity) / original_perplexity
  return(omni_result(TRUE, value = list(degradation_pct = round(degradation * 100, 2))))
}
