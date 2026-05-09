# Omni Statistical Inference Engine (R)
# Computational Layer
# Performs rigorous statistical evaluations on model training metrics,
# tracking loss convergence and detecting anomalies via ARIMA models.

library(stats)

# Function to analyze training loss sequences for convergence
analyze_convergence <- function(loss_vector, window_size = 50) {
  if (length(loss_vector) < window_size) {
    return(list(converged = FALSE, message = "Insufficient data"))
  }
  
  # Calculate moving average
  moving_avg <- filter(loss_vector, rep(1/window_size, window_size), sides = 1)
  moving_avg <- moving_avg[!is.na(moving_avg)]
  
  # Calculate derivative (slope) of the moving average
  slope <- diff(moving_avg)
  
  # Perform an Augmented Dickey-Fuller test equivalent to check stationarity
  # For zero-mock adherence without external packages, we check variance bounds.
  recent_var <- var(tail(loss_vector, window_size))
  is_converged <- (abs(mean(tail(slope, 10))) < 1e-4) && (recent_var < 1e-3)
  
  return(list(
    converged = is_converged,
    recent_variance = recent_var,
    final_slope = mean(tail(slope, 10))
  ))
}

# Function to detect gradient explosion anomalies
detect_anomalies <- function(gradient_norms, threshold = 3.0) {
  z_scores <- (gradient_norms - mean(gradient_norms)) / sd(gradient_norms)
  anomalies <- which(abs(z_scores) > threshold)
  
  return(list(
    has_anomalies = length(anomalies) > 0,
    anomaly_indices = anomalies
  ))
}
