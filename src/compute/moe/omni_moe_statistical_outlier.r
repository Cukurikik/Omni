# OMNI MOTHER Production Zero-Mock Statistical Outlier Detection
# Utilizes Median Absolute Deviation (MAD) to detect anomalous latency spikes
# in hardware cluster reports, triggering automated node eviction.

detect_latency_anomalies <- function(latencies_ms) {
  if (length(latencies_ms) < 10) {
    # Not enough data points to establish a baseline
    return(rep(FALSE, length(latencies_ms)))
  }
  
  # Calculate Median
  median_val <- median(latencies_ms, na.rm = TRUE)
  
  # Calculate Median Absolute Deviation (MAD)
  # MAD = median(|x_i - median(X)|)
  abs_dev <- abs(latencies_ms - median_val)
  mad_val <- median(abs_dev, na.rm = TRUE)
  
  # Prevent division by zero if all values are identical
  if (mad_val == 0) {
    mad_val <- 1e-6
  }
  
  # Compute Modified Z-Scores
  # Constant 0.6745 scales MAD to the standard deviation of normal distribution
  modified_z_scores <- (0.6745 * (latencies_ms - median_val)) / mad_val
  
  # Threshold > 3.5 is considered an outlier (Iglewicz and Hoaglin)
  is_outlier <- abs(modified_z_scores) > 3.5
  
  return(is_outlier)
}

# Example usage interface for Omni Mother API
process_cluster_health <- function(latency_vector) {
  outliers <- detect_latency_anomalies(latency_vector)
  
  if (any(outliers)) {
    cat(sprintf("OMNI CRITICAL: %d latency anomalies detected in cluster.\n", sum(outliers)))
    # Output indices of failing nodes
    print(which(outliers))
    return(FALSE) # Health check failed
  }
  
  return(TRUE) # Cluster healthy
}
