# Omni LooGLE Long-Context Stats (R)
omni_loogle_f1 <- function(pred_tokens, ref_tokens) {
  tp <- length(intersect(pred_tokens, ref_tokens))
  p <- tp / max(length(pred_tokens), 1); r <- tp / max(length(ref_tokens), 1)
  if (p + r == 0) 0 else round(2 * p * r / (p + r), 4)
}
omni_loogle_by_bucket <- function(results_df) {
  results_df$bucket <- ifelse(results_df$ctx_len < 4096, "short",
                        ifelse(results_df$ctx_len < 16384, "medium", "long"))
  aggregate(f1 ~ bucket, data = results_df, FUN = function(x) round(mean(x), 4))
}
