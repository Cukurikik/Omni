# DriveLM Visual QA Scorer — R statistical metrics
omni_result <- function(is_ok, value = NULL, error = NULL) {
  list(is_ok = is_ok, value = value, error = error)
}
compute_vqa_accuracy <- function(predictions, ground_truth) {
  if (length(predictions) != length(ground_truth)) {
    return(omni_result(FALSE, error = "Prediction/GT length mismatch"))
  }
  if (length(predictions) > 1000000) {
    return(omni_result(FALSE, error = "Exceeds 1M sample limit"))
  }
  matches <- sum(predictions == ground_truth)
  acc <- matches / length(predictions)
  return(omni_result(TRUE, value = acc))
}
compute_bleu_1gram <- function(candidate, reference) {
  if (nchar(candidate) > 10000 || nchar(reference) > 10000) {
    return(omni_result(FALSE, error = "Text exceeds 10K char limit"))
  }
  c_tokens <- strsplit(tolower(candidate), "\\s+")[[1]]
  r_tokens <- strsplit(tolower(reference), "\\s+")[[1]]
  if (length(c_tokens) == 0) return(omni_result(TRUE, value = 0.0))
  matches <- sum(c_tokens %in% r_tokens)
  precision <- matches / length(c_tokens)
  bp <- min(1.0, exp(1 - length(r_tokens) / max(1, length(c_tokens))))
  return(omni_result(TRUE, value = bp * precision))
}
