# Omni SelfAware ECE Stats (R)
# Ref: yinzhangyue/SelfAware
omni_ece <- function(confidences, correct, n_bins = 10) {
  bins <- cut(confidences, breaks = seq(0, 1, length.out = n_bins + 1), include.lowest = TRUE)
  total <- length(confidences)
  ece <- 0
  for (b in levels(bins)) {
    idx <- which(bins == b)
    if (length(idx) == 0) next
    avg_conf <- mean(confidences[idx])
    acc <- mean(correct[idx])
    ece <- ece + length(idx) / total * abs(avg_conf - acc)
  }
  ece
}
