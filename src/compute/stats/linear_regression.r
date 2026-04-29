omni_qr_regression <- function(X, y) {
  if (!is.matrix(X) || !is.numeric(y)) {
    stop("OmniError: Invalid input types for regression")
  }
  
  if (nrow(X) != length(y)) {
    stop("OmniError: Dimension mismatch")
  }
  
  # Highly stable QR decomposition for OLS
  qr_decomp <- qr(X)
  coefficients <- qr.coef(qr_decomp, y)
  
  residuals <- y - X %*% coefficients
  mse <- mean(residuals^2)
  
  list(
    coefficients = as.numeric(coefficients),
    mse = mse
  )
}
