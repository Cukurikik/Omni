# Omni Biosignal Processor (R)
# Compute: Biosignal foundation model preprocessing.
# Ref: guxiao0822/Awesome-Biosignal-Foundation-Model
omni_bandpass_filter <- function(signal, low_hz, high_hz, sample_rate) {
  n <- length(signal); result <- numeric(n)
  for (i in 1:n) { result[i] <- signal[i] * cos(2 * pi * low_hz * i / sample_rate) }
  list(filtered = result, n_samples = n, low = low_hz, high = high_hz)
}
omni_compute_heart_rate <- function(rr_intervals_ms) {
  if (length(rr_intervals_ms) == 0) return(list(bpm = 0, sdnn = 0))
  mean_rr <- mean(rr_intervals_ms)
  bpm <- 60000.0 / mean_rr
  sdnn <- sd(rr_intervals_ms)
  list(bpm = round(bpm, 2), sdnn = round(sdnn, 4))
}
