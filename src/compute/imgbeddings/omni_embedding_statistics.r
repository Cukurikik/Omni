# @omni-layer Compute | @omni-source minimaxir/imgbeddings | @omni-lang R
# @omni-description Image embedding statistics: distributional analysis of
# CLIP embeddings with dimensionality metrics and outlier detection.

omni_embedding_distribution <- function(embeddings) {
  if (nrow(embeddings) == 0) return(list(error = "No embeddings"))
  norms <- sqrt(rowSums(embeddings^2))
  dim_means <- colMeans(embeddings)
  dim_vars <- apply(embeddings, 2, var)
  # Effective dimensionality via participation ratio
  eigenvalues <- svd(scale(embeddings, center = TRUE, scale = FALSE))$d^2
  eigenvalues <- eigenvalues / sum(eigenvalues)
  participation_ratio <- sum(eigenvalues)^2 / sum(eigenvalues^2)
  list(
    data = list(
      n_samples = nrow(embeddings),
      n_dims = ncol(embeddings),
      mean_norm = mean(norms),
      sd_norm = sd(norms),
      min_norm = min(norms),
      max_norm = max(norms),
      effective_dim = participation_ratio,
      entropy = -sum(eigenvalues * log2(eigenvalues + 1e-10)),
      top_3_variance_explained = cumsum(sort(eigenvalues, decreasing = TRUE))[min(3, length(eigenvalues))]
    )
  )
}

omni_outlier_detection <- function(embeddings, threshold = 3.0) {
  if (nrow(embeddings) < 3) return(list(error = "Too few samples"))
  norms <- sqrt(rowSums(embeddings^2))
  mean_norm <- mean(norms)
  sd_norm <- sd(norms)
  z_scores <- abs((norms - mean_norm) / (sd_norm + 1e-8))
  outlier_mask <- z_scores > threshold
  list(
    data = list(
      n_samples = nrow(embeddings),
      n_outliers = sum(outlier_mask),
      outlier_rate = mean(outlier_mask),
      threshold = threshold,
      outlier_indices = which(outlier_mask),
      max_z_score = max(z_scores),
      mean_z_score = mean(z_scores)
    )
  )
}

omni_pairwise_diversity <- function(embeddings, sample_size = 100) {
  n <- nrow(embeddings)
  if (n < 2) return(list(error = "Too few samples"))
  n_pairs <- min(sample_size, n * (n - 1) / 2)
  sims <- numeric(n_pairs)
  idx <- 1
  for (i in 1:(n-1)) {
    for (j in (i+1):n) {
      if (idx > n_pairs) break
      dot <- sum(embeddings[i,] * embeddings[j,])
      ni <- sqrt(sum(embeddings[i,]^2) + 1e-8)
      nj <- sqrt(sum(embeddings[j,]^2) + 1e-8)
      sims[idx] <- dot / (ni * nj)
      idx <- idx + 1
    }
    if (idx > n_pairs) break
  }
  sims <- sims[1:min(idx-1, n_pairs)]
  list(
    data = list(
      n_pairs = length(sims),
      mean_similarity = mean(sims),
      sd_similarity = sd(sims),
      diversity_score = 1 - mean(sims)
    )
  )
}
