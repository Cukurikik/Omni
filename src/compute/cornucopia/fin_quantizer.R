OmniResult <- R6::R6Class("OmniResult",
  public = list(
    value = NULL,
    error = NULL,
    is_ok = FALSE,
    initialize = function(value = NULL, error = NULL) {
      self$value <- value
      self$error <- error
      self$is_ok <- is.null(error)
    }
  )
)

quantize_financial_series <- function(timeseries, levels) {
  if (length(timeseries) == 0 || levels <= 1) {
    return(OmniResult$new(error = "Invalid financial timeseries or levels"))
  }
  
  # Cornucopia-specific financial quantization math
  min_val <- min(timeseries)
  max_val <- max(timeseries)
  step <- (max_val - min_val) / levels
  
  quantized <- round((timeseries - min_val) / step)
  
  return(OmniResult$new(value = quantized))
}
