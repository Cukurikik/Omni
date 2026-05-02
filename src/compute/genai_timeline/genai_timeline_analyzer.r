# @omni-domain Compute Layer (GenAI Timeline)
# @omni-source various/genai-timeline
# @omni-description GenAI Timeline Analyzer mimicking temporal trend analysis in R.
# @omni-requirement zero-mock, monadic-error

omni_result <- function(data = NULL, error = NULL) {
  list(data = data, error = error, is_ok = is.null(error))
}

genai_timeline_analyzer <- list(
  compute_trend = function(dates, values) {
    if (length(dates) == 0 || length(values) == 0) {
      return(omni_result(error = "Dates and values cannot be empty."))
    }
    if (length(dates) != length(values)) {
      return(omni_result(error = "Dates and values must have same length."))
    }
    n <- length(values)
    x <- seq_len(n)
    x_mean <- mean(x)
    y_mean <- mean(values)
    ss_xy <- sum((x - x_mean) * (values - y_mean))
    ss_xx <- sum((x - x_mean)^2)
    if (ss_xx == 0) {
      return(omni_result(error = "Variance is zero, cannot compute trend."))
    }
    slope <- ss_xy / ss_xx
    intercept <- y_mean - slope * x_mean
    fitted <- intercept + slope * x
    residuals <- values - fitted
    ss_res <- sum(residuals^2)
    ss_tot <- sum((values - y_mean)^2)
    r_squared <- 1 - (ss_res / max(ss_tot, 1e-10))
    direction <- ifelse(slope > 0, "increasing", ifelse(slope < 0, "decreasing", "flat"))
    omni_result(data = list(
      slope = slope, intercept = intercept, r_squared = r_squared,
      direction = direction, fitted = fitted
    ))
  },
  compute_moving_average = function(values, window = 7) {
    if (length(values) < window) {
      return(omni_result(error = "Not enough data points for window size."))
    }
    ma <- numeric(length(values) - window + 1)
    for (i in seq_along(ma)) {
      ma[i] <- mean(values[i:(i + window - 1)])
    }
    omni_result(data = list(moving_average = ma, window = window))
  }
)
