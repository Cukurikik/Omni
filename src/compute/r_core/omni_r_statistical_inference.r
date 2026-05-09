# OMNI Compute Layer: R Statistical Inference
omni_inference <- function(data) {
  model <- lm(y ~ x, data=data)
  return(summary(model))
}
