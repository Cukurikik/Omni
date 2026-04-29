# Efficient LLM Quantization Metrics — R
omni_result <- function(is_ok, value = NULL, error = NULL) {
  list(is_ok = is_ok, value = value, error = error)
}
compute_perplexity <- function(log_probs) {
  if (length(log_probs) == 0) return(omni_result(FALSE, error = "Empty log_probs"))
  if (length(log_probs) > 10000000) return(omni_result(FALSE, error = "Exceeds 10M token limit"))
  avg_nll <- -mean(log_probs)
  ppl <- exp(avg_nll)
  if (is.nan(ppl) || is.infinite(ppl)) return(omni_result(FALSE, error = "NaN/Inf perplexity"))
  return(omni_result(TRUE, value = ppl))
}
