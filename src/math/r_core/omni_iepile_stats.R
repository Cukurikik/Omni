# Omni IEPile Stats (R)
# Statistical analysis layer for Information Extraction evaluation.

omni_compute_f1_score <- function(precision, recall) {
  # Monadic error return pattern
  if (precision < 0 || precision > 1 || recall < 0 || recall > 1) {
    return(list(success = FALSE, error = "Metrics must be bounded [0,1]", value = NA))
  }
  
  if (precision + recall == 0) {
    return(list(success = TRUE, error = NA, value = 0.0))
  }
  
  f1 <- 2 * (precision * recall) / (precision + recall)
  return(list(success = TRUE, error = NA, value = f1))
}
