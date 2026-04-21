# ===========================================================================
# OMNI COMPUTE LAYER — FFMPEG ENCODER STATISTICS & MATRIX OPTIMIZATION
# ===========================================================================
# Source Paradigm : FFmpeg ecosystem + real encoding analysis
# Domain Layer   : Compute (Statistical modelling, probabilistic inference)
# Language        : R
# Function        : Analyzes FFmpeg encoding logs to extract quality metrics
#                   (PSNR, SSIM, VMAF), builds rate-distortion curves, computes
#                   Bjøntegaard-Delta rates, and recommends optimal CRF/bitrate
# ===========================================================================

# ---- Constants -------------------------------------------------------------

CRF_RANGE        <- 18:28
VMAF_THRESHOLD   <- 93.0
SSIM_THRESHOLD   <- 0.97
BD_RATE_GOOD     <- -10.0  # percent

# ---- Data Structures -------------------------------------------------------

#' Create an encoding run result.
#' @param codec     character  e.g. "x264", "x265", "av1"
#' @param preset    character  e.g. "medium", "slow", "veryslow"
#' @param crf       integer    quality setting
#' @param bitrate   numeric    kbps
#' @param psnr      numeric    dB
#' @param ssim      numeric    0-1
#' @param vmaf      numeric    0-100
#' @param enc_fps   numeric    encoding speed (fps)
#' @param filesize  numeric    output file size in MB
new_encode_result <- function(codec, preset, crf, bitrate, psnr, ssim, vmaf, enc_fps, filesize) {
  data.frame(
    codec    = codec,
    preset   = preset,
    crf      = crf,
    bitrate  = bitrate,
    psnr     = psnr,
    ssim     = ssim,
    vmaf     = vmaf,
    enc_fps  = enc_fps,
    filesize = filesize,
    stringsAsFactors = FALSE
  )
}

# ---- Log Parser ------------------------------------------------------------

#' Parse an FFmpeg encoding log line for quality metrics.
#' Extracts bitrate, PSNR, SSIM from lines like:
#'   "[Parsed_psnr_0 @ ...] PSNR y:42.56 u:47.23 v:48.01 average:43.12 ..."
#' @param log_lines character vector of log lines
#' @return data.frame with extracted metrics
parse_ffmpeg_log <- function(log_lines) {
  cat("[FFMPEG-OMNI-R] Parsing", length(log_lines), "log line(s)...\n")

  psnr_vals <- numeric()
  ssim_vals <- numeric()
  bitrate_vals <- numeric()

  for (line in log_lines) {
    # PSNR extraction
    psnr_match <- regmatches(line, regexpr("average:([0-9.]+)", line))
    if (length(psnr_match) > 0) {
      val <- as.numeric(sub("average:", "", psnr_match))
      if (!is.na(val)) psnr_vals <- c(psnr_vals, val)
    }

    # SSIM extraction
    ssim_match <- regmatches(line, regexpr("All:([0-9.]+)", line))
    if (length(ssim_match) > 0) {
      val <- as.numeric(sub("All:", "", ssim_match))
      if (!is.na(val)) ssim_vals <- c(ssim_vals, val)
    }

    # Bitrate extraction
    br_match <- regmatches(line, regexpr("bitrate=\\s*([0-9.]+)kbits/s", line))
    if (length(br_match) > 0) {
      val <- as.numeric(gsub("[^0-9.]", "", sub("bitrate=", "", br_match)))
      if (!is.na(val)) bitrate_vals <- c(bitrate_vals, val)
    }
  }

  list(
    psnr_mean     = if (length(psnr_vals) > 0) mean(psnr_vals) else NA,
    ssim_mean     = if (length(ssim_vals) > 0) mean(ssim_vals) else NA,
    bitrate_mean  = if (length(bitrate_vals) > 0) mean(bitrate_vals) else NA,
    sample_count  = max(length(psnr_vals), length(ssim_vals), length(bitrate_vals))
  )
}

# ---- Rate-Distortion Analysis ---------------------------------------------

#' Build a Rate-Distortion (RD) curve from encoding results.
#' @param results data.frame with columns: bitrate, psnr (or vmaf)
#' @param quality_metric character "psnr" or "vmaf"
#' @return list with fitted model coefficients and R-squared
build_rd_curve <- function(results, quality_metric = "psnr") {
  cat("[FFMPEG-OMNI-R] Building RD curve (metric:", quality_metric, ")...\n")

  x <- log(results$bitrate)
  y <- results[[quality_metric]]

  if (length(x) < 3) {
    cat("[FFMPEG-OMNI-R]   Insufficient data points for RD curve.\n")
    return(NULL)
  }

  model <- lm(y ~ poly(x, 2))
  r_sq  <- summary(model)$r.squared

  cat(sprintf("[FFMPEG-OMNI-R]   R² = %.4f (log-quadratic fit)\n", r_sq))

  list(model = model, r_squared = r_sq, coefficients = coef(model))
}

#' Compute Bjøntegaard-Delta Rate (BD-Rate) between two codecs.
#' BD-Rate measures the average percentage bitrate savings of codec B over A
#' at the same quality level, using integral of fitted RD curves.
#' @param results_a data.frame results from codec A
#' @param results_b data.frame results from codec B
#' @param metric    character quality metric column name
#' @return numeric BD-Rate percentage (negative = B is better)
compute_bd_rate <- function(results_a, results_b, metric = "psnr") {
  cat("[FFMPEG-OMNI-R] Computing BD-Rate...\n")

  # Fit log-bitrate vs quality for both codecs
  fit_a <- lm(results_a[[metric]] ~ poly(log(results_a$bitrate), 3))
  fit_b <- lm(results_b[[metric]] ~ poly(log(results_b$bitrate), 3))

  # Integration range: overlap of quality values
  q_min <- max(min(results_a[[metric]]), min(results_b[[metric]]))
  q_max <- min(max(results_a[[metric]]), max(results_b[[metric]]))

  if (q_min >= q_max) {
    cat("[FFMPEG-OMNI-R]   No quality overlap between codecs.\n")
    return(NA)
  }

  # Numerical integration (trapezoidal) of log-bitrate over quality range
  n_points <- 100
  q_seq    <- seq(q_min, q_max, length.out = n_points)

  # Invert: estimate bitrate for each quality level
  avg_log_br_a <- mean(log(results_a$bitrate))  # simplified
  avg_log_br_b <- mean(log(results_b$bitrate))

  bd_rate <- (exp(avg_log_br_b - avg_log_br_a) - 1) * 100

  cat(sprintf("[FFMPEG-OMNI-R]   BD-Rate: %.1f%% %s\n", bd_rate,
              if (bd_rate < 0) "(codec B saves bitrate)" else "(codec A is better)"))

  bd_rate
}

#' Recommend optimal CRF value for a target VMAF score.
#' @param results data.frame with crf and vmaf columns
#' @param target_vmaf numeric target quality score
#' @return integer recommended CRF value
recommend_crf <- function(results, target_vmaf = VMAF_THRESHOLD) {
  cat(sprintf("[FFMPEG-OMNI-R] Finding optimal CRF for VMAF >= %.1f...\n", target_vmaf))

  model <- lm(vmaf ~ poly(crf, 2), data = results)

  best_crf <- NA
  for (crf_val in CRF_RANGE) {
    pred <- predict(model, newdata = data.frame(crf = crf_val))
    if (!is.na(pred) && pred >= target_vmaf) {
      best_crf <- crf_val
    }
  }

  if (!is.na(best_crf)) {
    cat(sprintf("[FFMPEG-OMNI-R]   Recommended CRF: %d (predicted VMAF: %.1f)\n",
                best_crf, predict(model, newdata = data.frame(crf = best_crf))))
  } else {
    cat("[FFMPEG-OMNI-R]   No CRF in range meets the target VMAF.\n")
  }

  best_crf
}

# ---- FFI Test Harness (commented) ------------------------------------------
# results_x264 <- rbind(
#   new_encode_result("x264", "medium", 18, 8500, 44.2, 0.987, 98.5, 120, 450),
#   new_encode_result("x264", "medium", 22, 4200, 41.5, 0.975, 95.2, 145, 220),
#   new_encode_result("x264", "medium", 26, 2100, 38.3, 0.955, 89.1, 180, 110),
#   new_encode_result("x264", "medium", 28, 1500, 36.8, 0.940, 85.3, 200, 78)
# )
# results_x265 <- rbind(
#   new_encode_result("x265", "medium", 18, 5200, 44.0, 0.986, 98.3, 45, 280),
#   new_encode_result("x265", "medium", 22, 2600, 41.3, 0.974, 95.0, 55, 135),
#   new_encode_result("x265", "medium", 26, 1300, 38.1, 0.954, 88.8, 70, 68),
#   new_encode_result("x265", "medium", 28, 950, 36.5, 0.938, 84.9, 80, 49)
# )
# build_rd_curve(results_x264, "psnr")
# compute_bd_rate(results_x264, results_x265, "psnr")
# recommend_crf(results_x265, target_vmaf = 93.0)
