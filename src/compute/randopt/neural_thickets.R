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

analyze_thicket_density <- function(weight_matrix, threshold = 0.05) {
  if (is.null(weight_matrix)) {
    return(OmniResult$new(error = "Invalid weight matrix"))
  }
  
  # R math for RandOpt Neural Thickets density analysis
  density <- sum(abs(weight_matrix) > threshold) / length(weight_matrix)
  
  return(OmniResult$new(value = density))
}
