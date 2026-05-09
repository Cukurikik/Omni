# moe_survey_balance_metrics.r — Compute Layer: MoE Survey Balance Metrics
# R script calculating advanced statistical distributions of expert loads.

calculate_gini_coefficient <- function(expert_loads) {
  # Calculate Gini coefficient to measure expert inequality
  n <- length(expert_loads)
  if (n == 0) return(0)
  
  loads_sorted <- sort(expert_loads)
  index <- 1:n
  
  sum_loads <- sum(loads_sorted)
  if (sum_loads == 0) return(0)
  
  gini <- (2 * sum(index * loads_sorted) / (n * sum_loads)) - ((n + 1) / n)
  return(gini)
}

analyze_routing_distribution <- function(load_matrix) {
  # Load matrix where rows are batches and columns are experts
  total_loads <- colSums(load_matrix)
  
  gini <- calculate_gini_coefficient(total_loads)
  variance <- var(total_loads)
  mean_load <- mean(total_loads)
  
  results <- list(
    Gini_Coefficient = gini,
    Variance = variance,
    Mean_Load = mean_load,
    Is_Balanced = (gini < 0.2) # Threshold for "balanced" routing
  )
  
  return(results)
}
