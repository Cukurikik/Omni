# OMNI R Compute Layer for TonicValidate Metrics
# Bounded statistical processing for validation scores

suppressPackageStartupMessages(library(stats))
suppressPackageStartupMessages(library(jsonlite))

#' Compute bounded confidence intervals for LLM validation scores
#' @param scores Numeric vector of scores [0, 1]
#' @param conf_level Confidence level (default 0.95)
#' @return List with status and payload (monadic design)
compute_tonic_stats <- function(scores, conf_level = 0.95) {
  # Hardware/Resource Bound: max 1M scores
  if (length(scores) > 1000000) {
    return(list(status = "Error", error = "OMNI_LIMIT: Max score count exceeded (1M limit)"))
  }
  
  if (length(scores) < 2) {
    return(list(status = "Error", error = "OMNI_ERROR: Insufficient data for stats"))
  }
  
  if (any(scores < 0 | scores > 1)) {
    return(list(status = "Error", error = "OMNI_ERROR: Scores out of bounds [0, 1]"))
  }
  
  mean_val <- mean(scores)
  std_err <- sd(scores) / sqrt(length(scores))
  error_margin <- qt(conf_level + (1 - conf_level) / 2, df = length(scores) - 1) * std_err
  
  result <- list(
    status = "Ok",
    payload = list(
      mean = mean_val,
      lower_bound = max(0, mean_val - error_margin),
      upper_bound = min(1, mean_val + error_margin),
      variance = var(scores)
    )
  )
  return(result)
}

# FFI Entry
execute_stat_compute <- function(json_payload) {
  data <- fromJSON(json_payload)
  res <- compute_tonic_stats(data$scores)
  return(toJSON(res, auto_unbox = TRUE))
}
