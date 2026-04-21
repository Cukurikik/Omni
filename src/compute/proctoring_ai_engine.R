# ===========================================================================
# OMNI COMPUTE LAYER — PROCTORING AI ANOMALY DETECTION ENGINE
# ===========================================================================
# Source Paradigm : vardanagarwal/Proctoring-AI (face_detector.py, gaze, head_pose)
# Domain Layer   : Compute (Statistical modelling, CV inference)
# Language        : R
# Function        : Statistical anomaly scoring for exam proctoring — face
#                   detection confidence analysis, gaze deviation measurement,
#                   head pose estimation, and multi-metric cheat-score fusion
# ===========================================================================

# ---- Configuration ---------------------------------------------------------

FACE_CONFIDENCE_THRESHOLD <- 0.5
GAZE_DEVIATION_LIMIT      <- 15.0   # degrees from center
HEAD_YAW_LIMIT            <- 25.0   # degrees
HEAD_PITCH_LIMIT          <- 20.0
BLINK_RATE_NORMAL         <- c(15, 25)  # blinks per minute range
CHEAT_SCORE_ALERT         <- 0.65

# ---- Data Structures -------------------------------------------------------

#' Create a single frame observation for proctoring analysis.
#' @param frame_id     integer  sequential frame number
#' @param timestamp_ms numeric  milliseconds since session start
#' @param face_conf    numeric  face detection confidence (0-1)
#' @param face_count   integer  number of faces detected
#' @param gaze_yaw     numeric  horizontal gaze deviation (degrees)
#' @param gaze_pitch   numeric  vertical gaze deviation (degrees)
#' @param head_yaw     numeric  head rotation yaw (degrees)
#' @param head_pitch   numeric  head rotation pitch (degrees)
#' @param head_roll    numeric  head rotation roll (degrees)
#' @param blink_state  logical  TRUE if eyes closed this frame
new_frame_obs <- function(frame_id, timestamp_ms, face_conf, face_count,
                          gaze_yaw, gaze_pitch, head_yaw, head_pitch,
                          head_roll, blink_state) {
  list(
    frame_id     = frame_id,
    timestamp_ms = timestamp_ms,
    face_conf    = face_conf,
    face_count   = face_count,
    gaze_yaw     = gaze_yaw,
    gaze_pitch   = gaze_pitch,
    head_yaw     = head_yaw,
    head_pitch   = head_pitch,
    head_roll    = head_roll,
    blink_state  = blink_state
  )
}

# ---- Core Analysis Functions -----------------------------------------------

#' Detect face anomalies from a detection confidence stream.
#' Mirrors Proctoring-AI find_faces() threshold logic.
#'
#' @param confidences numeric vector of per-frame face confidences
#' @return list(no_face_frames, multi_face_frames, avg_confidence)
analyze_face_presence <- function(observations) {
  cat("[PROCTOR-OMNI-R] Analyzing face presence across", length(observations), "frames...\n")

  confs  <- sapply(observations, function(o) o$face_conf)
  counts <- sapply(observations, function(o) o$face_count)

  no_face    <- sum(confs < FACE_CONFIDENCE_THRESHOLD)
  multi_face <- sum(counts > 1)
  avg_conf   <- mean(confs)

  cat(sprintf("[PROCTOR-OMNI-R]   No-face frames: %d | Multi-face: %d | Avg conf: %.3f\n",
              no_face, multi_face, avg_conf))

  list(no_face_frames = no_face, multi_face_frames = multi_face, avg_confidence = avg_conf)
}

#' Compute gaze deviation score — how far the student looks away from screen.
#' Based on Proctoring-AI gaze_scoring.py eye aspect ratio logic.
#'
#' @param observations list of frame observations
#' @return list(mean_deviation, max_deviation, off_screen_pct)
analyze_gaze <- function(observations) {
  cat("[PROCTOR-OMNI-R] Analyzing gaze deviation...\n")

  deviations <- sapply(observations, function(o) {
    sqrt(o$gaze_yaw^2 + o$gaze_pitch^2)
  })

  off_screen <- sum(deviations > GAZE_DEVIATION_LIMIT)
  pct        <- off_screen / length(observations) * 100

  cat(sprintf("[PROCTOR-OMNI-R]   Mean deviation: %.2f° | Max: %.2f° | Off-screen: %.1f%%\n",
              mean(deviations), max(deviations), pct))

  list(mean_deviation = mean(deviations), max_deviation = max(deviations), off_screen_pct = pct)
}

#' Estimate head pose anomalies — excessive rotation suggests looking away.
#' Mirrors Proctoring-AI head_pose_estimation.py.
#'
#' @param observations list of frame observations
#' @return list(yaw_violations, pitch_violations, roll_std)
analyze_head_pose <- function(observations) {
  cat("[PROCTOR-OMNI-R] Analyzing head pose...\n")

  yaws    <- sapply(observations, function(o) o$head_yaw)
  pitches <- sapply(observations, function(o) o$head_pitch)
  rolls   <- sapply(observations, function(o) o$head_roll)

  yaw_v   <- sum(abs(yaws) > HEAD_YAW_LIMIT)
  pitch_v <- sum(abs(pitches) > HEAD_PITCH_LIMIT)
  roll_sd <- sd(rolls)

  cat(sprintf("[PROCTOR-OMNI-R]   Yaw violations: %d | Pitch violations: %d | Roll SD: %.2f°\n",
              yaw_v, pitch_v, roll_sd))

  list(yaw_violations = yaw_v, pitch_violations = pitch_v, roll_std = roll_sd)
}

#' Compute blink rate and detect prolonged eye closure.
#' @param observations list of frame observations
#' @param fps          numeric frames per second
#' @return list(blink_rate_per_min, prolonged_closures)
analyze_blinks <- function(observations, fps = 30) {
  cat("[PROCTOR-OMNI-R] Analyzing blink patterns...\n")

  blinks <- sapply(observations, function(o) o$blink_state)
  total_time_min <- length(observations) / fps / 60

  # Count blink transitions (open→closed)
  transitions <- sum(diff(as.integer(blinks)) == 1)
  rate <- if (total_time_min > 0) transitions / total_time_min else 0

  # Detect prolonged closures (>0.5s = >15 consecutive frames at 30fps)
  rle_result <- rle(blinks)
  prolonged  <- sum(rle_result$lengths[rle_result$values] > (fps / 2))

  abnormal <- rate < BLINK_RATE_NORMAL[1] || rate > BLINK_RATE_NORMAL[2]

  cat(sprintf("[PROCTOR-OMNI-R]   Blink rate: %.1f/min %s | Prolonged closures: %d\n",
              rate, if (abnormal) "(ABNORMAL)" else "(normal)", prolonged))

  list(blink_rate_per_min = rate, prolonged_closures = prolonged, is_abnormal = abnormal)
}

#' Fuse all sub-scores into a single cheat probability score.
#' @return numeric cheat_score in [0, 1]
compute_cheat_score <- function(face_result, gaze_result, head_result, blink_result, n_frames) {
  cat("[PROCTOR-OMNI-R] Computing fused cheat score...\n")

  # Weighted scoring (production: calibrated via logistic regression)
  face_penalty <- (face_result$no_face_frames + face_result$multi_face_frames * 2) / n_frames
  gaze_penalty <- gaze_result$off_screen_pct / 100
  head_penalty <- (head_result$yaw_violations + head_result$pitch_violations) / n_frames
  blink_penalty <- if (blink_result$is_abnormal) 0.15 else 0

  score <- 0.30 * face_penalty + 0.35 * gaze_penalty + 0.25 * head_penalty + 0.10 * blink_penalty
  score <- min(max(score, 0), 1)  # clamp [0,1]

  if (score > CHEAT_SCORE_ALERT) {
    cat(sprintf("[PROCTOR-OMNI-R]   ⚠ ALERT: Cheat score %.3f exceeds threshold %.2f!\n",
                score, CHEAT_SCORE_ALERT))
  } else {
    cat(sprintf("[PROCTOR-OMNI-R]   ✓ Cheat score: %.3f (below threshold)\n", score))
  }

  score
}

# ---- FFI Test Harness (commented) ------------------------------------------
# set.seed(42)
# n <- 300
# obs <- lapply(1:n, function(i) {
#   new_frame_obs(
#     frame_id = i, timestamp_ms = i * 33,
#     face_conf = runif(1, 0.3, 1.0), face_count = sample(0:2, 1, prob=c(0.05,0.90,0.05)),
#     gaze_yaw = rnorm(1, 0, 8), gaze_pitch = rnorm(1, 0, 5),
#     head_yaw = rnorm(1, 0, 12), head_pitch = rnorm(1, 0, 8), head_roll = rnorm(1, 0, 3),
#     blink_state = sample(c(TRUE,FALSE), 1, prob=c(0.05, 0.95))
#   )
# })
# fr <- analyze_face_presence(obs)
# gr <- analyze_gaze(obs)
# hr <- analyze_head_pose(obs)
# br <- analyze_blinks(obs)
# compute_cheat_score(fr, gr, hr, br, n)
