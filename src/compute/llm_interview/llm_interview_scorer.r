# @omni-domain Compute Layer (LLM Interview)
# @omni-source various/llm-interview
# @omni-description LLM Interview Scorer mimicking evaluation metrics in R.
# @omni-requirement zero-mock, monadic-error

omni_result <- function(data = NULL, error = NULL) {
  list(data = data, error = error, is_ok = is.null(error))
}

llm_interview_scorer <- list(
  compute_bleu = function(reference, hypothesis) {
    if (nchar(reference) == 0 || nchar(hypothesis) == 0) {
      return(omni_result(error = "Reference and hypothesis cannot be empty."))
    }
    ref_words <- strsplit(tolower(reference), "\\s+")[[1]]
    hyp_words <- strsplit(tolower(hypothesis), "\\s+")[[1]]
    matches <- sum(hyp_words %in% ref_words)
    precision <- matches / max(length(hyp_words), 1)
    bp <- ifelse(length(hyp_words) >= length(ref_words), 1.0, exp(1 - length(ref_words) / max(length(hyp_words), 1)))
    bleu <- bp * precision
    omni_result(data = list(bleu = bleu, precision = precision, brevity_penalty = bp))
  },
  compute_rouge_l = function(reference, hypothesis) {
    if (nchar(reference) == 0 || nchar(hypothesis) == 0) {
      return(omni_result(error = "Reference and hypothesis cannot be empty."))
    }
    ref_words <- strsplit(tolower(reference), "\\s+")[[1]]
    hyp_words <- strsplit(tolower(hypothesis), "\\s+")[[1]]
    m <- length(ref_words)
    n <- length(hyp_words)
    lcs_table <- matrix(0, nrow = m + 1, ncol = n + 1)
    for (i in seq_len(m)) {
      for (j in seq_len(n)) {
        if (ref_words[i] == hyp_words[j]) {
          lcs_table[i + 1, j + 1] <- lcs_table[i, j] + 1
        } else {
          lcs_table[i + 1, j + 1] <- max(lcs_table[i, j + 1], lcs_table[i + 1, j])
        }
      }
    }
    lcs_len <- lcs_table[m + 1, n + 1]
    recall <- lcs_len / max(m, 1)
    precision <- lcs_len / max(n, 1)
    f1 <- ifelse(precision + recall > 0, 2 * precision * recall / (precision + recall), 0)
    omni_result(data = list(rouge_l = f1, precision = precision, recall = recall, lcs_length = lcs_len))
  }
)
