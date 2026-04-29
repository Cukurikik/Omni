# Omni UHGEval Hallucination Stats (R)
omni_hallucination_ratio <- function(response_tokens, reference_tokens) {
  ungrounded <- setdiff(response_tokens, reference_tokens)
  round(length(ungrounded) / max(length(response_tokens), 1), 4)
}
omni_uhg_benchmark <- function(scores_df) {
  list(mean_score = round(mean(scores_df$score), 4),
       min_score = round(min(scores_df$score), 4),
       max_score = round(max(scores_df$score), 4),
       n_tasks = nrow(scores_df))
}
omni_abstention_rate <- function(abstained, total) {
  round(abstained / max(total, 1), 4)
}
