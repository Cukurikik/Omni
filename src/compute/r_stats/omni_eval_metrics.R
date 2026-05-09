// OMNI Compute — R Statistical Model Evaluation
# Comprehensive evaluation metrics for LLM performance.
library(stats)

omni_compute_metrics <- function(predictions, references) {
  n <- length(predictions)
  stopifnot(n == length(references), n > 0)
  
  correct <- sum(predictions == references)
  accuracy <- correct / n
  se <- sqrt(accuracy * (1 - accuracy) / n)
  
  ci_lower <- accuracy - 1.96 * se
  ci_upper <- accuracy + 1.96 * se
  
  list(
    accuracy = accuracy,
    correct = correct,
    total = n,
    std_error = se,
    ci_95 = c(lower = max(0, ci_lower), upper = min(1, ci_upper))
  )
}

omni_perplexity <- function(log_probs) {
  n <- length(log_probs)
  stopifnot(n > 0)
  avg_nll <- -mean(log_probs)
  ppl <- exp(avg_nll)
  list(perplexity = ppl, avg_nll = avg_nll, n_tokens = n)
}

omni_bleu_score <- function(candidate, reference, max_n = 4) {
  cand_tokens <- strsplit(tolower(candidate), "\\s+")[[1]]
  ref_tokens <- strsplit(tolower(reference), "\\s+")[[1]]
  
  precisions <- numeric(max_n)
  for (n in 1:max_n) {
    if (length(cand_tokens) < n) { precisions[n] <- 0; next }
    cand_ngrams <- sapply(1:(length(cand_tokens) - n + 1), function(i) paste(cand_tokens[i:(i+n-1)], collapse=" "))
    ref_ngrams <- sapply(1:(length(ref_tokens) - n + 1), function(i) paste(ref_tokens[i:(i+n-1)], collapse=" "))
    matches <- sum(cand_ngrams %in% ref_ngrams)
    precisions[n] <- matches / max(length(cand_ngrams), 1)
  }
  
  bp <- ifelse(length(cand_tokens) >= length(ref_tokens), 1, exp(1 - length(ref_tokens) / length(cand_tokens)))
  geo_mean <- exp(mean(log(pmax(precisions, 1e-10))))
  bleu <- bp * geo_mean
  
  list(bleu = bleu, brevity_penalty = bp, precisions = precisions)
}

omni_rouge_l <- function(candidate, reference) {
  cand <- strsplit(tolower(candidate), "\\s+")[[1]]
  ref <- strsplit(tolower(reference), "\\s+")[[1]]
  
  m <- length(cand); n <- length(ref)
  lcs_table <- matrix(0, m + 1, n + 1)
  for (i in 1:m) for (j in 1:n) {
    if (cand[i] == ref[j]) lcs_table[i+1, j+1] <- lcs_table[i, j] + 1
    else lcs_table[i+1, j+1] <- max(lcs_table[i, j+1], lcs_table[i+1, j])
  }
  
  lcs_len <- lcs_table[m+1, n+1]
  precision <- lcs_len / max(m, 1)
  recall <- lcs_len / max(n, 1)
  f1 <- ifelse(precision + recall > 0, 2 * precision * recall / (precision + recall), 0)
  
  list(rouge_l = f1, precision = precision, recall = recall, lcs_length = lcs_len)
}

omni_eval_report <- function(predictions, references, log_probs = NULL) {
  acc <- omni_compute_metrics(predictions, references)
  report <- list(accuracy = acc)
  if (!is.null(log_probs)) report$perplexity <- omni_perplexity(log_probs)
  report$timestamp <- Sys.time()
  report
}
