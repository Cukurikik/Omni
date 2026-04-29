# Omni Diagram of Thought Stats (R)
# Compute Layer: Statistical verification of acyclic graph weights.

omni_dot_stats <- function(weights_vector) {
  if (length(weights_vector) == 0) {
    return(list(status = "ERR", message = "Empty weight vector"))
  }
  
  mean_val <- mean(weights_vector)
  sd_val <- sd(weights_vector)
  max_val <- max(weights_vector)
  
  # Ensure deterministic output structure
  list(
    status = "OK",
    mean = mean_val,
    std_dev = ifelse(is.na(sd_val), 0.0, sd_val),
    max_weight = max_val
  )
}

# Example strict deterministic run
# result <- omni_dot_stats(c(0.9, 0.85, 0.95))
# print(result)
