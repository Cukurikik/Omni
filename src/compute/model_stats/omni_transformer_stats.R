# @omni-layer Compute | @omni-lang R | @omni-batch 18 | @omni-semester 16
# @omni-description Statistical analysis of transformer model performance:
# forecasting accuracy metrics, attention distribution analysis, calibration.

library(stats)

#' Compute forecasting accuracy metrics
#' @param actual numeric vector of actual values
#' @param predicted numeric vector of predicted values
#' @return named list of metrics
compute_forecast_metrics <- function(actual, predicted) {
  n <- length(actual)
  stopifnot(n == length(predicted), n > 0)

  residuals <- actual - predicted
  mae <- mean(abs(residuals))
  mse <- mean(residuals^2)
  rmse <- sqrt(mse)
  mape <- mean(abs(residuals / (actual + 1e-10))) * 100
  smape <- mean(2 * abs(residuals) / (abs(actual) + abs(predicted) + 1e-10)) * 100

  ss_res <- sum(residuals^2)
  ss_tot <- sum((actual - mean(actual))^2)
  r_squared <- 1 - ss_res / (ss_tot + 1e-10)

  list(
    mae = mae, mse = mse, rmse = rmse,
    mape = mape, smape = smape, r_squared = r_squared,
    n = n
  )
}

#' Analyze attention distribution entropy
#' @param attention_weights matrix of attention weights (n x n)
#' @return named list with entropy stats
analyze_attention_entropy <- function(attention_weights) {
  n <- nrow(attention_weights)
  entropies <- numeric(n)

  for (i in 1:n) {
    probs <- attention_weights[i, ]
    probs <- pmax(probs, 1e-10)
    probs <- probs / sum(probs)
    entropies[i] <- -sum(probs * log2(probs))
  }

  max_entropy <- log2(n)

  list(
    mean_entropy = mean(entropies),
    std_entropy = sd(entropies),
    min_entropy = min(entropies),
    max_entropy_observed = max(entropies),
    max_entropy_possible = max_entropy,
    normalized_entropy = mean(entropies) / max_entropy,
    is_uniform = mean(entropies) > 0.9 * max_entropy,
    per_token_entropy = entropies
  )
}

#' Model calibration analysis (reliability diagram data)
#' @param predicted_probs numeric vector of predicted probabilities
#' @param actual_labels binary vector (0/1) of actual outcomes
#' @param n_bins number of calibration bins
#' @return data.frame for reliability diagram
calibration_analysis <- function(predicted_probs, actual_labels, n_bins = 10) {
  bins <- cut(predicted_probs, breaks = seq(0, 1, length.out = n_bins + 1), include.lowest = TRUE)

  result <- data.frame(
    bin = levels(bins),
    mean_predicted = numeric(n_bins),
    mean_actual = numeric(n_bins),
    count = numeric(n_bins),
    stringsAsFactors = FALSE
  )

  for (i in 1:n_bins) {
    mask <- as.integer(bins) == i
    if (sum(mask) > 0) {
      result$mean_predicted[i] <- mean(predicted_probs[mask])
      result$mean_actual[i] <- mean(actual_labels[mask])
      result$count[i] <- sum(mask)
    }
  }

  ece <- sum(result$count * abs(result$mean_predicted - result$mean_actual)) / sum(result$count)

  attr(result, "ece") <- ece
  attr(result, "n_bins") <- n_bins
  result
}

#' Compare multiple model performances
#' @param models named list of model predictions
#' @param actual actual values
#' @return data.frame of comparative metrics
compare_models <- function(models, actual) {
  results <- data.frame(
    model = character(0),
    mae = numeric(0), rmse = numeric(0),
    mape = numeric(0), r_squared = numeric(0),
    stringsAsFactors = FALSE
  )

  for (name in names(models)) {
    m <- compute_forecast_metrics(actual, models[[name]])
    results <- rbind(results, data.frame(
      model = name, mae = m$mae, rmse = m$rmse,
      mape = m$mape, r_squared = m$r_squared,
      stringsAsFactors = FALSE
    ))
  }

  results[order(results$rmse), ]
}
