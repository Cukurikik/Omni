# @omni-layer Compute | @omni-source OscarKjell/text | @omni-lang R
# @omni-description Text embedding analytics in R: cosine similarity matrix,
# PCA projection, and cluster-based text analysis using transformer embeddings.

omni_cosine_matrix <- function(embeddings) {
  n <- nrow(embeddings)
  mat <- matrix(0, nrow = n, ncol = n)
  norms <- sqrt(rowSums(embeddings^2) + 1e-8)
  for (i in seq_len(n)) {
    for (j in i:n) {
      sim <- sum(embeddings[i, ] * embeddings[j, ]) / (norms[i] * norms[j])
      mat[i, j] <- sim; mat[j, i] <- sim
    }
  }
  list(data = list(matrix = mat, n = n, mean_sim = mean(mat[upper.tri(mat)])))
}

omni_pca_project <- function(embeddings, n_components = 2) {
  centered <- scale(embeddings, center = TRUE, scale = FALSE)
  svd_result <- svd(centered, nu = n_components, nv = n_components)
  projected <- centered %*% svd_result$v[, seq_len(n_components)]
  variance_explained <- svd_result$d^2 / sum(svd_result$d^2)
  list(
    data = list(
      projected = projected,
      variance_explained = variance_explained[seq_len(n_components)],
      total_variance = sum(variance_explained[seq_len(n_components)]),
      n_samples = nrow(embeddings),
      n_components = n_components
    )
  )
}

omni_text_cluster <- function(embeddings, k = 3) {
  if (nrow(embeddings) < k) return(list(error = "Too few samples"))
  km <- kmeans(embeddings, centers = k, nstart = 10)
  list(
    data = list(
      clusters = km$cluster,
      centers = km$centers,
      n_clusters = k,
      within_ss = km$tot.withinss,
      between_ss = km$betweenss,
      sizes = km$size
    )
  )
}

omni_embedding_stats <- function(embeddings) {
  list(
    data = list(
      n_samples = nrow(embeddings),
      n_dims = ncol(embeddings),
      mean_norm = mean(sqrt(rowSums(embeddings^2))),
      sd_norm = sd(sqrt(rowSums(embeddings^2))),
      dim_means = colMeans(embeddings),
      dim_sds = apply(embeddings, 2, sd)
    )
  )
}
