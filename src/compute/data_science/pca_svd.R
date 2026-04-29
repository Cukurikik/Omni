# OMNI DATA SCIENCE: Principal Component Analysis (PCA) via SVD
# Pure mathematical implementation using Singular Value Decomposition.
# Source: CodeCutTech/Data-science

omni_pca <- function(X, n_components) {
  # Input validation
  if (!is.matrix(X)) {
    return(list(error = "Input X must be a matrix."))
  }
  
  if (n_components > ncol(X)) {
    return(list(error = "n_components cannot be greater than number of features."))
  }
  
  # Step 1: Center the data (mean 0)
  n <- nrow(X)
  col_means <- colMeans(X)
  X_centered <- scale(X, center = col_means, scale = FALSE)
  
  # Step 2: Singular Value Decomposition (SVD)
  # X_centered = U * D * V^T
  svd_res <- svd(X_centered)
  
  # Step 3: Extract principal components (V matrix)
  components <- svd_res$v[, 1:n_components]
  
  # Step 4: Project the data onto the principal components
  projected_X <- X_centered %*% components
  
  # Step 5: Calculate explained variance ratio
  eigenvalues <- (svd_res$d^2) / (n - 1)
  explained_variance_ratio <- eigenvalues[1:n_components] / sum(eigenvalues)
  
  # Return successful result structure
  return(list(
    projected = projected_X,
    components = components,
    explained_variance_ratio = explained_variance_ratio,
    error = NULL
  ))
}

# Example usage:
# data_matrix <- matrix(rnorm(100), nrow=20, ncol=5)
# result <- omni_pca(data_matrix, n_components=2)
