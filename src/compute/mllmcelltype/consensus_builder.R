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

build_cell_consensus <- function(llm_predictions_matrix) {
  if (nrow(llm_predictions_matrix) == 0 || ncol(llm_predictions_matrix) == 0) {
    return(OmniResult$new(error = "Empty predictions matrix"))
  }
  
  # mLLMCelltype multi-LLM consensus math using mode voting per cell
  consensus <- apply(llm_predictions_matrix, 1, function(x) {
    ux <- unique(x)
    ux[which.max(tabulate(match(x, ux)))]
  })
  
  return(OmniResult$new(value = consensus))
}
