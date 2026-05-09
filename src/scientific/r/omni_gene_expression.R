# OMNI Framework - Gene Expression Clustering (R)
# Preprocesses RNA-seq data before ingestion by the Bioinformatics Transformer

library(stats)

# Function to perform basic K-Means clustering on Gene Expression Matrix
omni_cluster_genes <- function(expression_matrix, k_clusters=5) {
  print(paste("OMNI R: Running K-Means clustering with k =", k_clusters))
  
  # Ensure matrix is numeric
  if(!is.numeric(expression_matrix)) {
    stop("OMNI R: Expression matrix must be numeric.")
  }
  
  # Scale data (z-score normalization)
  scaled_data <- scale(expression_matrix)
  
  # Perform K-Means
  set.seed(42) # Reproducibility
  km_res <- kmeans(scaled_data, centers=k_clusters, nstart=25)
  
  print("OMNI R: Clustering complete.")
  
  return(list(
    cluster_assignments = km_res$cluster,
    centers = km_res$centers
  ))
}

# Example usage (Mock data)
# data <- matrix(rnorm(1000), nrow=100, ncol=10) # 100 genes, 10 samples
# result <- omni_cluster_genes(data, k_clusters=3)
# print(table(result$cluster_assignments))
