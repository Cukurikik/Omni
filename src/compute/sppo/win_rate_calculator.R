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

calculate_win_rate <- function(wins, total_matches) {
  if (total_matches <= 0) {
    return(OmniResult$new(error = "Total matches must be > 0"))
  }
  
  # R math for SPPO win rate calculation with Laplace smoothing
  win_rate <- (wins + 1) / (total_matches + 2)
  
  return(OmniResult$new(value = win_rate))
}
