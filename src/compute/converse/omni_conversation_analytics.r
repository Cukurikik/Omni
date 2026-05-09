# @omni-layer Compute | @omni-source maxent-ai/converse
# @omni-description Conversation analytics in R: topic coherence, sentiment flow,
# speaker dominance, and interaction quality metrics.
# @omni-lang R | @omni-batch 16 | @omni-semester 16

omni_conversation_analytics <- function(turn_sentiments, speakers) {
  n <- length(turn_sentiments)
  if (n == 0) return(list(error = "No turns"))
  speaker_table <- table(speakers)
  dominance <- as.list(speaker_table / n)
  sentiment_flow <- diff(turn_sentiments)
  volatility <- sd(sentiment_flow)
  trajectory <- lm(turn_sentiments ~ seq_along(turn_sentiments))
  trend_slope <- coef(trajectory)[2]
  resolution <- if (!is.na(trend_slope) && trend_slope > 0) "improving" else "declining"
  speaker_sentiment <- tapply(turn_sentiments, speakers, mean, na.rm = TRUE)
  agreement <- 1 - sd(speaker_sentiment, na.rm = TRUE)
  list(
    data = list(
      n_turns = n,
      n_speakers = length(unique(speakers)),
      speaker_dominance = dominance,
      sentiment_volatility = volatility,
      trend_slope = trend_slope,
      resolution = resolution,
      agreement_score = max(0, agreement),
      mean_sentiment = mean(turn_sentiments),
      speaker_sentiments = as.list(speaker_sentiment)
    )
  )
}

omni_topic_coherence <- function(topic_distributions) {
  n <- nrow(topic_distributions)
  if (is.null(n) || n < 2) return(list(error = "Need >= 2 distributions"))
  coherence_scores <- numeric(n - 1)
  for (i in 2:n) {
    p <- topic_distributions[i, ]
    q <- topic_distributions[i - 1, ]
    p_norm <- p / sum(p + 1e-8)
    q_norm <- q / sum(q + 1e-8)
    kl <- sum(p_norm * log((p_norm + 1e-8) / (q_norm + 1e-8)))
    coherence_scores[i - 1] <- exp(-kl)
  }
  list(
    data = list(
      coherence_scores = coherence_scores,
      mean_coherence = mean(coherence_scores),
      min_coherence = min(coherence_scores),
      topic_shift_points = which(coherence_scores < 0.5)
    )
  )
}
