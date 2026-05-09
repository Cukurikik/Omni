# @omni-layer Compute | @omni-source microsoft/GPTQ-for-LLaMa | @omni-lang R
# @omni-description Quantization quality analysis: MSE, SNR, and distribution
# comparison between FP32 and INT4 weight representations.
# @omni-lang R | @omni-batch 16 | @omni-semester 16

omni_quant_quality <- function(original, quantized) {
  if (length(original) != length(quantized)) {
    return(list(error = "Length mismatch"))
  }
  n <- length(original)
  diff <- original - quantized
  mse <- mean(diff^2)
  rmse <- sqrt(mse)
  signal_power <- mean(original^2)
  snr_db <- if (mse > 0) 10 * log10(signal_power / mse) else Inf
  max_error <- max(abs(diff))
  cosine_sim <- sum(original * quantized) /
    (sqrt(sum(original^2)) * sqrt(sum(quantized^2)) + 1e-8)
  ks_test <- ks.test(original, quantized)
  list(
    data = list(
      mse = mse,
      rmse = rmse,
      snr_db = snr_db,
      max_error = max_error,
      cosine_similarity = cosine_sim,
      ks_statistic = ks_test$statistic,
      ks_p_value = ks_test$p.value,
      n_params = n,
      compression_ratio = 32 / 4,
      original_mean = mean(original),
      quantized_mean = mean(quantized),
      original_sd = sd(original),
      quantized_sd = sd(quantized)
    )
  )
}

omni_quant_layer_analysis <- function(layer_weights, bits = 4, group_size = 128) {
  n <- length(layer_weights)
  n_groups <- ceiling(n / group_size)
  group_stats <- lapply(seq_len(n_groups), function(g) {
    start <- (g - 1) * group_size + 1
    end <- min(g * group_size, n)
    chunk <- layer_weights[start:end]
    list(
      group = g,
      range = max(chunk) - min(chunk),
      mean = mean(chunk),
      sd = sd(chunk)
    )
  })
  list(
    data = list(
      n_groups = n_groups,
      group_size = group_size,
      bits = bits,
      avg_range = mean(sapply(group_stats, `[[`, "range")),
      max_range = max(sapply(group_stats, `[[`, "range")),
      memory_bytes = ceiling(n * bits / 8) + n_groups * 8
    )
  )
}
