# ===========================================================================
# OMNI BAYESIAN ENGINE (SEMESTER 3 — BATCH 38.6)
# ===========================================================================
# Absorbed From  : R rstanarm + brms + MCMCpack + bayesplot concepts
# Logic Inherited: R / Compute Layer (Bayesian Inference via MCMC)
# ===========================================================================
#
# By studying MCMCpack and brms, Mother learned:
#   1. Metropolis-Hastings samples from posterior distributions
#   2. Gibbs sampling cycles through conditional distributions
#   3. Prior * Likelihood = Posterior (Bayes theorem)
#   4. Burn-in period discards initial non-convergent samples
#   5. Effective sample size (ESS) measures MCMC efficiency

# ============================================================
# PART 1: Metropolis-Hastings MCMC Sampler
# ============================================================

#' Metropolis-Hastings MCMC sampler.
#'
#' @param log_posterior Function computing log(posterior)
#' @param initial Starting parameter values (numeric vector)
#' @param proposal_sd Standard deviations for Gaussian proposals
#' @param n_iter Total iterations
#' @param burn_in Number of initial samples to discard
#' @param thin Thinning interval (keep every thin-th sample)
#' @return List with samples, acceptance rate, and diagnostics
omni_mcmc <- function(log_posterior, initial, proposal_sd,
                       n_iter = 10000, burn_in = 1000, thin = 1) {
  n_params <- length(initial)
  stopifnot(length(proposal_sd) == n_params)

  # Storage
  total_samples <- ceiling((n_iter - burn_in) / thin)
  samples <- matrix(NA, nrow = total_samples, ncol = n_params)
  log_posteriors <- numeric(total_samples)

  current <- initial
  current_lp <- log_posterior(current)
  accepted <- 0
  total_proposals <- 0
  sample_idx <- 0

  for (iter in seq_len(n_iter)) {
    # Propose new parameters (symmetric Gaussian proposal)
    proposed <- current + rnorm(n_params, mean = 0, sd = proposal_sd)

    # Compute log acceptance ratio
    proposed_lp <- log_posterior(proposed)
    log_alpha <- proposed_lp - current_lp

    total_proposals <- total_proposals + 1

    # Accept/reject
    if (log(runif(1)) < log_alpha) {
      current <- proposed
      current_lp <- proposed_lp
      accepted <- accepted + 1
    }

    # Store sample (after burn-in, with thinning)
    if (iter > burn_in && (iter - burn_in) %% thin == 0) {
      sample_idx <- sample_idx + 1
      if (sample_idx <= total_samples) {
        samples[sample_idx, ] <- current
        log_posteriors[sample_idx] <- current_lp
      }
    }
  }

  # Trim to actual samples
  samples <- samples[seq_len(sample_idx), , drop = FALSE]
  log_posteriors <- log_posteriors[seq_len(sample_idx)]

  list(
    samples = samples,
    log_posteriors = log_posteriors,
    acceptance_rate = accepted / total_proposals,
    n_samples = sample_idx,
    n_params = n_params,
    burn_in = burn_in,
    thin = thin,
    call = match.call()
  )
}

# ============================================================
# PART 2: Posterior Summary Statistics
# ============================================================

#' Summarize MCMC posterior samples.
omni_mcmc_summary <- function(mcmc_result, param_names = NULL,
                               credible_level = 0.95) {
  samples <- mcmc_result$samples
  n_params <- ncol(samples)

  if (is.null(param_names)) {
    param_names <- paste0("param_", seq_len(n_params))
  }

  alpha <- 1 - credible_level

  summary_df <- data.frame(
    parameter = param_names,
    mean = apply(samples, 2, mean),
    median = apply(samples, 2, median),
    sd = apply(samples, 2, sd),
    ci_lower = apply(samples, 2, quantile, probs = alpha / 2),
    ci_upper = apply(samples, 2, quantile, probs = 1 - alpha / 2),
    ess = apply(samples, 2, omni_ess),
    rhat = apply(samples, 2, function(x) omni_rhat(matrix(x, ncol = 1))),
    stringsAsFactors = FALSE
  )

  cat("\nOmni Bayesian Posterior Summary\n")
  cat("================================\n")
  cat(sprintf("Acceptance rate: %.1f%%\n", mcmc_result$acceptance_rate * 100))
  cat(sprintf("Credible level: %.0f%%\n", credible_level * 100))
  cat(sprintf("Total samples: %d\n\n", mcmc_result$n_samples))
  print(summary_df, digits = 4, row.names = FALSE)

  invisible(summary_df)
}

# ============================================================
# PART 3: MCMC Diagnostics
# ============================================================

#' Effective Sample Size (ESS) using autocorrelation
omni_ess <- function(x) {
  n <- length(x)
  if (n < 4) return(n)

  # Compute autocorrelation
  acf_vals <- acf(x, lag.max = min(n - 1, 500), plot = FALSE)$acf[-1]

  # Sum consecutive pairs of autocorrelations (Geyer's method)
  tau <- 1
  for (i in seq(1, length(acf_vals) - 1, by = 2)) {
    pair_sum <- acf_vals[i] + ifelse(i + 1 <= length(acf_vals), acf_vals[i + 1], 0)
    if (pair_sum < 0) break
    tau <- tau + 2 * pair_sum
  }

  max(1, n / tau)
}

#' R-hat convergence diagnostic (simplified)
omni_rhat <- function(samples_matrix) {
  if (ncol(samples_matrix) == 1) {
    # Split chain in half for single-chain R-hat
    n <- nrow(samples_matrix)
    half <- floor(n / 2)
    chain1 <- samples_matrix[1:half, 1]
    chain2 <- samples_matrix[(half+1):n, 1]
  } else {
    chain1 <- samples_matrix[, 1]
    chain2 <- samples_matrix[, 2]
  }

  n1 <- length(chain1)
  n2 <- length(chain2)

  # Within-chain variance
  W <- (var(chain1) * (n1 - 1) / n1 + var(chain2) * (n2 - 1) / n2) / 2

  # Between-chain variance
  grand_mean <- mean(c(chain1, chain2))
  B <- ((mean(chain1) - grand_mean)^2 + (mean(chain2) - grand_mean)^2) * min(n1, n2)

  # R-hat
  V <- W * (min(n1, n2) - 1) / min(n1, n2) + B / min(n1, n2)
  if (W == 0) return(1.0)

  sqrt(V / W)
}

# ============================================================
# PART 4: Conjugate Bayesian Models
# ============================================================

#' Beta-Binomial conjugate model
omni_beta_binomial <- function(successes, trials,
                                prior_alpha = 1, prior_beta = 1) {
  post_alpha <- prior_alpha + successes
  post_beta <- prior_beta + (trials - successes)

  list(
    prior = list(alpha = prior_alpha, beta = prior_beta),
    posterior = list(alpha = post_alpha, beta = post_beta),
    posterior_mean = post_alpha / (post_alpha + post_beta),
    posterior_mode = ifelse(post_alpha > 1 & post_beta > 1,
                           (post_alpha - 1) / (post_alpha + post_beta - 2), NA),
    ci_95 = qbeta(c(0.025, 0.975), post_alpha, post_beta),
    evidence = lbeta(post_alpha, post_beta) - lbeta(prior_alpha, prior_beta)
  )
}

#' Normal-Normal conjugate model (known variance)
omni_normal_conjugate <- function(data, known_var,
                                   prior_mean = 0, prior_var = 100) {
  n <- length(data)
  data_mean <- mean(data)

  # Posterior precision = prior precision + data precision
  prior_prec <- 1 / prior_var
  data_prec <- n / known_var
  post_prec <- prior_prec + data_prec

  post_var <- 1 / post_prec
  post_mean <- post_var * (prior_prec * prior_mean + data_prec * data_mean)

  list(
    prior = list(mean = prior_mean, var = prior_var),
    posterior = list(mean = post_mean, var = post_var),
    posterior_sd = sqrt(post_var),
    ci_95 = qnorm(c(0.025, 0.975), post_mean, sqrt(post_var)),
    shrinkage = data_prec / post_prec,
    bf_vs_prior = dnorm(data_mean, prior_mean, sqrt(prior_var + known_var/n), log = TRUE)
  )
}

# ============================================================
# Engine Diagnostics
# ============================================================

omni_bayesian_diagnostics <- function() {
  list(
    engine = "OmniBayesianEngine",
    layer = "R Compute",
    capabilities = c(
      "omni_mcmc (Metropolis-Hastings)",
      "omni_mcmc_summary (posterior summary)",
      "omni_ess (effective sample size)",
      "omni_rhat (convergence diagnostic)",
      "omni_beta_binomial (conjugate Beta-Binomial)",
      "omni_normal_conjugate (conjugate Normal-Normal)"
    ),
    learned_logic = c(
      "metropolis-hastings-accept-reject",
      "log-posterior-numerical-stability",
      "burn-in-discard-transient",
      "thinning-reduce-autocorrelation",
      "ess-geyer-pair-sum-method",
      "rhat-split-chain-convergence",
      "conjugate-prior-closed-form",
      "bayes-factor-model-comparison"
    )
  )
}
