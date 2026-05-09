# @omni-layer Compute | @omni-source calebevans/cordon | @omni-lang R
# @omni-description Log statistics engine: statistical analysis of log
# frequency patterns, anomaly distributions, and template clustering.

omni_log_frequency_analysis <- function(template_counts) {
  if (length(template_counts) == 0) return(list(error = "No data"))
  sorted <- sort(template_counts, decreasing = TRUE)
  total <- sum(sorted)
  n <- length(sorted)
  cumulative <- cumsum(sorted) / total
  # Zipf analysis
  ranks <- seq_len(n)
  log_ranks <- log(ranks)
  log_counts <- log(sorted + 1)
  if (n >= 2) {
    zipf_fit <- lm(log_counts ~ log_ranks)
    zipf_exponent <- -coef(zipf_fit)[2]
  } else {
    zipf_exponent <- NA
  }
  list(
    data = list(
      n_templates = n,
      total_occurrences = total,
      top_10_pct_coverage = if (n >= 1) cumulative[max(1, ceiling(n*0.1))] else 0,
      top_50_pct_coverage = if (n >= 1) cumulative[max(1, ceiling(n*0.5))] else 0,
      zipf_exponent = zipf_exponent,
      entropy = -sum((sorted/total) * log2(sorted/total + 1e-10)),
      mean_count = mean(sorted),
      median_count = median(sorted),
      sd_count = sd(sorted)
    )
  )
}

omni_anomaly_distribution <- function(scores, threshold = 0.3) {
  if (length(scores) == 0) return(list(error = "No scores"))
  anomalies <- scores[scores > threshold]
  normals <- scores[scores <= threshold]
  ks_result <- if (length(anomalies) >= 2 && length(normals) >= 2) {
    ks.test(anomalies, normals)
  } else {
    list(statistic = NA, p.value = NA)
  }
  list(
    data = list(
      total_scores = length(scores),
      n_anomalies = length(anomalies),
      anomaly_rate = length(anomalies) / length(scores),
      mean_anomaly_score = if (length(anomalies) > 0) mean(anomalies) else 0,
      mean_normal_score = if (length(normals) > 0) mean(normals) else 0,
      ks_statistic = ks_result$statistic,
      ks_pvalue = ks_result$p.value,
      score_quantiles = quantile(scores, probs = c(0.25, 0.5, 0.75, 0.90, 0.95, 0.99))
    )
  )
}

omni_temporal_log_pattern <- function(timestamps, window_minutes = 5) {
  if (length(timestamps) < 2) return(list(error = "Too few timestamps"))
  ts <- as.POSIXct(timestamps, origin = "1970-01-01")
  diffs <- diff(as.numeric(ts))
  list(
    data = list(
      n_events = length(timestamps),
      avg_interval_sec = mean(diffs),
      sd_interval_sec = sd(diffs),
      min_interval_sec = min(diffs),
      max_interval_sec = max(diffs),
      events_per_minute = length(timestamps) / (max(as.numeric(ts)) - min(as.numeric(ts))) * 60,
      burst_threshold = mean(diffs) - 2 * sd(diffs)
    )
  )
}
