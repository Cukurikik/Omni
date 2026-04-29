OmniResult <- R6::R6Class("OmniResult",
  public = list(
    value = NULL,
    error = NULL,
    is_ok = FALSE,
    initialize = function(value = NULL, error = NULL) {
      self$value <- value
      self$error <- error
      self$is_ok <- is.null(error)
    }
  )
)

retrieve_hierarchical <- function(query_vec, graph_matrix) {
  if (is.null(query_vec) || is.null(graph_matrix)) {
    return(OmniResult$new(error = "Invalid inputs"))
  }
  
  # R statistical computation for HiRAG hierarchical retrieval
  scores <- colSums(query_vec * graph_matrix)
  
  return(OmniResult$new(value = scores))
}
