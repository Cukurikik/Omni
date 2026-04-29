# OMNI R Compute Layer for Fuzz4All Coverage Statistics
# Bounded statistical summary of execution paths hit during fuzzing

#' Compute bounded coverage statistics
#' @param total_paths Integer total executable paths
#' @param hit_paths Integer paths hit during fuzzing
#' @return List with status and payload
compute_coverage_stats <- function(total_paths, hit_paths) {
  if (total_paths <= 0) {
    return(list(status = "Error", error = "OMNI_MATH_ERR: Total paths must be > 0"))
  }
  
  if (hit_paths < 0 || hit_paths > total_paths) {
    return(list(status = "Error", error = "OMNI_DATA_ERR: Hit paths must be between 0 and total paths"))
  }
  
  coverage_percentage <- (hit_paths / total_paths) * 100.0
  
  # Assess quality of fuzzing round
  quality <- "Low"
  if (coverage_percentage >= 80.0) {
    quality <- "High"
  } else if (coverage_percentage >= 50.0) {
    quality <- "Medium"
  }
  
  result <- list(
    status = "Ok",
    payload = list(
      coverage_pct = coverage_percentage,
      quality = quality,
      missed_paths = total_paths - hit_paths
    )
  )
  return(result)
}
