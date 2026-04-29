# Omni Sentiment Stats (R)
# Compute Layer: Statistical analysis of sentiment reasoning distributions.
# Ref: leduckhai/Sentiment-Reasoning — ACL 2025

omni_sentiment_stats <- function(scores, labels) {
  if (length(scores) != length(labels) || length(scores) == 0) {
    return(list(status = "ERR", message = "Mismatched or empty inputs"))
  }
  list(
    status = "OK",
    mean_score = mean(scores),
    sd_score = sd(scores),
    label_distribution = table(labels)
  )
}
