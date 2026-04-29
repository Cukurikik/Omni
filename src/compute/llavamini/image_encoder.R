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

encode_image_features <- function(image_matrix) {
  if (is.null(image_matrix)) {
    return(OmniResult$new(error = "Invalid image matrix"))
  }
  
  # R math for image feature vector generation
  features <- colMeans(image_matrix)
  
  return(OmniResult$new(value = features))
}
