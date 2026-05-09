# moe_polygenic_risk_score.r — Compute
# Layer: Compute — Polygenic Risk Score (PRS) using MoE
# Inspired by: moe-prs-paper (Mixture-of-Experts PRS)

# OMNI R Expert: Computes ensemble Polygenic Risk Scores over genetic variants

calculate_moe_prs <- function(genotype_matrix, expert_weights_list, routing_probs) {
  # genotype_matrix: N individuals x M SNPs
  # expert_weights_list: List of K weight vectors (each of length M)
  # routing_probs: N x K matrix of probabilities assigning individuals to experts
  
  num_individuals <- nrow(genotype_matrix)
  num_experts <- length(expert_weights_list)
  
  if (ncol(routing_probs) != num_experts || nrow(routing_probs) != num_individuals) {
    stop("Dimension mismatch in routing probabilities.")
  }
  
  final_prs <- numeric(num_individuals)
  
  for (k in 1:num_experts) {
    # Calculate PRS for expert K
    expert_prs <- genotype_matrix %*% expert_weights_list[[k]]
    
    # Weight the prediction by the routing probability (soft routing)
    final_prs <- final_prs + (expert_prs * routing_probs[, k])
  }
  
  return(final_prs)
}

# Example validation logic (Zero-Mock strictness)
validate_genotypes <- function(genotype_matrix) {
  if(any(is.na(genotype_matrix))) {
    stop("Imputation required. NAs found in genotype matrix.")
  }
  if(max(genotype_matrix) > 2 || min(genotype_matrix) < 0) {
    stop("Genotypes must be encoded as 0, 1, or 2.")
  }
  return(TRUE)
}
