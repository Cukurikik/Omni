# ===========================================================================
# OMNI COMPUTE LAYER — GOOGLE IT AUTOMATION STATISTICAL AUDITOR
# ===========================================================================
# Source Paradigm : elmoallistair/google-it-automation
# Domain Layer   : Compute (Statistical modelling, probabilistic inference)
# Language        : R
# Function        : Applies statistical process control to IT automation
#                   metrics — CPU load, deployment frequency, error budgets
# ===========================================================================

# ---- Core Functions --------------------------------------------------------

#' Bootstrap the auditor and echo readiness.
google_it_audit_init <- function() {
  cat("[GOOGLE-IT-OMNI-R] Initializing IT-Automation Statistical Auditor...\n")
}

#' Detect anomalous deployment windows by comparing historical frequency
#' distributions against the latest sample.
#'
#' @param historical_deploys numeric vector of daily deploy counts (30+ days)
#' @param latest_sample      numeric vector of deploy counts for the audit window
#' @param confidence         z-score multiplier (default 2 = ~95% CI)
#' @return logical TRUE if the latest window is statistically anomalous
audit_deploy_frequency <- function(historical_deploys,
                                   latest_sample,
                                   confidence = 2.0) {
  cat("[GOOGLE-IT-OMNI-R] Auditing deployment frequency distribution...\n")

  mu    <- mean(historical_deploys)
  sigma <- sd(historical_deploys)
  latest_mu <- mean(latest_sample)

  z_score <- abs(latest_mu - mu) / sigma

  cat(sprintf("[GOOGLE-IT-OMNI-R] Historical: mean=%.2f  sd=%.2f\n", mu, sigma))
  cat(sprintf("[GOOGLE-IT-OMNI-R] Latest window: mean=%.2f  z=%.3f\n", latest_mu, z_score))

  anomalous <- z_score > confidence
  if (anomalous) {
    cat("[GOOGLE-IT-OMNI-R] ⚠ ANOMALY: Deploy rate deviates beyond confidence bound!\n")
  } else {
    cat("[GOOGLE-IT-OMNI-R] ✓ Deploy frequency within normal parameters.\n")
  }
  return(anomalous)
}

#' Compute an error-budget burn rate from SLO targets.
#'
#' @param total_requests  integer total requests in the window
#' @param failed_requests integer failed requests in the window
#' @param slo_target      numeric target availability (e.g. 0.999)
#' @return numeric  burn rate (>1 means over-burning)
compute_error_budget_burn <- function(total_requests,
                                      failed_requests,
                                      slo_target = 0.999) {
  cat("[GOOGLE-IT-OMNI-R] Computing SLO error-budget burn rate...\n")

  allowed_failures <- total_requests * (1 - slo_target)
  burn_rate <- failed_requests / allowed_failures

  cat(sprintf("[GOOGLE-IT-OMNI-R] Allowed failures: %.0f | Actual: %d | Burn: %.2fx\n",
              allowed_failures, failed_requests, burn_rate))

  if (burn_rate > 1.0) {
    cat("[GOOGLE-IT-OMNI-R] ⚠ CRITICAL: Error budget exhausted!\n")
  }
  return(burn_rate)
}

# ---- FFI Test Harness (commented out) --------------------------------------
# set.seed(42)
# historical <- rpois(60, lambda = 12)
# latest     <- rpois(7, lambda = 20)
#
# google_it_audit_init()
# audit_deploy_frequency(historical, latest)
# compute_error_budget_burn(total_requests = 1e6, failed_requests = 1200)
