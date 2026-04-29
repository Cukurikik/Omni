# Tango Mel-Spectrogram Statistics — R
omni_result <- function(is_ok, value = NULL, error = NULL) {
  list(is_ok = is_ok, value = value, error = error)
}
compute_mel_stats <- function(mel_matrix) {
  if (!is.matrix(mel_matrix)) return(omni_result(FALSE, error = "Input must be matrix"))
  if (nrow(mel_matrix) > 256 || ncol(mel_matrix) > 100000)
    return(omni_result(FALSE, error = "Mel dims out of bounds"))
  stats <- list(
    mean_energy = mean(mel_matrix),
    max_energy = max(mel_matrix),
    min_energy = min(mel_matrix),
    sd_energy = sd(as.vector(mel_matrix)),
    duration_frames = ncol(mel_matrix)
  )
  return(omni_result(TRUE, value = stats))
}
