# Omni MMStar VLM Benchmark Stats (R)
# Ref: MMStar-Benchmark/MMStar — NeurIPS 2024
omni_mmstar_accuracy <- function(predictions, answers) {
  correct <- sum(toupper(trimws(predictions)) == toupper(trimws(answers)))
  round(correct / max(length(answers), 1), 4)
}

omni_mmstar_by_capability <- function(results_df) {
  aggregate(correct ~ capability, data = results_df,
            FUN = function(x) round(mean(x), 4))
}

omni_mmstar_leakage_rate <- function(text_only_correct, total) {
  round(text_only_correct / max(total, 1), 4)
}
