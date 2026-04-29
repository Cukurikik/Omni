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

calculate_reward_decay <- function(rewards, gamma = 0.99) {
  if (length(rewards) == 0) {
    return(OmniResult$new(error = "Empty rewards array"))
  }
  
  # R math for RL discounted reward sum
  n <- length(rewards)
  discounts <- gamma ^ (0:(n-1))
  discounted_sum <- sum(rewards * discounts)
  
  return(OmniResult$new(value = discounted_sum))
}
