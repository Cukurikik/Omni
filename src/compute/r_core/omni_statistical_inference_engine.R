# ===========================================================================
# OMNI STATISTICAL INFERENCE ENGINE (SEMESTER 3 REMEDIATION — BATCH 38.1)
# ===========================================================================
# Absorbed From  : stats package + MASS + caret + bayesian concepts
# Logic Inherited: R / Compute Layer (Bayesian + Frequentist Inference)
# Domain Layer   : Compute (R Core)
# ===========================================================================
#
# By studying R's stats package and MASS, Mother learned that R's
# vectorized operations and formula interface enable concise statistical
# modeling that no other language matches:
#   1. Vectorized operations on entire columns (no loops)
#   2. Formula interface (y ~ x1 + x2) for model specification
#   3. S3 dispatch for polymorphic summary/predict methods
#   4. Built-in distributions (dnorm, pnorm, rbinom, etc.)
#
# R IS the language for statistical inference in OMNI's Compute Layer.

# ---- Core Statistical Functions ----

#' Compute descriptive statistics for a numeric vector.
#' Returns a named list of key summary measures.
#' @param x Numeric vector
#' @return Named list: mean, median, sd, var, min, max, q1, q3, iqr, skewness, kurtosis
omni_describe <- function(x) {
  stopifnot(is.numeric(x))
  x <- x[!is.na(x)]  # Remove NAs
  n <- length(x)
  
  mu <- mean(x)
  med <- median(x)
  s <- sd(x)
  v <- var(x)
  q <- quantile(x, probs = c(0.25, 0.75))
  
  # Skewness (Fisher's definition)
  m3 <- sum((x - mu)^3) / n
  skew <- m3 / (s^3)
  
  # Kurtosis (excess, Fisher's definition)
  m4 <- sum((x - mu)^4) / n
  kurt <- (m4 / (s^4)) - 3
  
  list(
    n = n,
    mean = mu,
    median = med,
    sd = s,
    variance = v,
    min = min(x),
    max = max(x),
    q1 = unname(q[1]),
    q3 = unname(q[2]),
    iqr = unname(q[2] - q[1]),
    skewness = skew,
    kurtosis = kurt
  )
}

# ---- Hypothesis Testing ----

#' Perform a two-sample t-test with Welch's correction.
#' Computes t-statistic, degrees of freedom (Welch-Satterthwaite),
#' and p-value from the t-distribution.
#' @param x Numeric vector (group 1)
#' @param y Numeric vector (group 2)
#' @param alpha Significance level (default 0.05)
#' @return Named list with test results
omni_welch_t_test <- function(x, y, alpha = 0.05) {
  stopifnot(is.numeric(x), is.numeric(y))
  x <- x[!is.na(x)]
  y <- y[!is.na(y)]
  
  n1 <- length(x); n2 <- length(y)
  m1 <- mean(x); m2 <- mean(y)
  v1 <- var(x); v2 <- var(y)
  
  # Welch's t-statistic
  se <- sqrt(v1 / n1 + v2 / n2)
  t_stat <- (m1 - m2) / se
  
  # Welch-Satterthwaite degrees of freedom
  num <- (v1 / n1 + v2 / n2)^2
  den <- (v1 / n1)^2 / (n1 - 1) + (v2 / n2)^2 / (n2 - 1)
  df <- num / den
  
  # Two-tailed p-value from t-distribution
  p_value <- 2 * pt(-abs(t_stat), df = df)
  
  list(
    test = "Welch Two-Sample t-test",
    t_statistic = t_stat,
    degrees_of_freedom = df,
    p_value = p_value,
    significant = p_value < alpha,
    alpha = alpha,
    mean_group1 = m1,
    mean_group2 = m2,
    mean_difference = m1 - m2,
    ci_lower = (m1 - m2) - qt(1 - alpha / 2, df) * se,
    ci_upper = (m1 - m2) + qt(1 - alpha / 2, df) * se
  )
}

# ---- Bayesian Inference ----

#' Bayesian inference for a proportion using Beta-Binomial conjugacy.
#' Prior: Beta(alpha_prior, beta_prior)
#' Likelihood: Binomial(n, p)
#' Posterior: Beta(alpha_prior + successes, beta_prior + failures)
#' @param successes Number of successes observed
#' @param trials Total number of trials
#' @param alpha_prior Prior alpha (default 1 = uniform)
#' @param beta_prior Prior beta (default 1 = uniform)
#' @return Named list with posterior parameters and credible interval
omni_bayesian_proportion <- function(successes, trials,
                                      alpha_prior = 1, beta_prior = 1) {
  stopifnot(successes >= 0, trials >= successes)
  
  failures <- trials - successes
  
  # Posterior parameters (conjugate update)
  alpha_post <- alpha_prior + successes
  beta_post <- beta_prior + failures
  
  # Posterior mean and variance
  post_mean <- alpha_post / (alpha_post + beta_post)
  post_var <- (alpha_post * beta_post) /
    ((alpha_post + beta_post)^2 * (alpha_post + beta_post + 1))
  
  # 95% Highest Density Interval (HDI) via quantiles
  hdi_lower <- qbeta(0.025, alpha_post, beta_post)
  hdi_upper <- qbeta(0.975, alpha_post, beta_post)
  
  list(
    method = "Beta-Binomial Conjugate Bayesian",
    prior = list(alpha = alpha_prior, beta = beta_prior),
    data = list(successes = successes, failures = failures, trials = trials),
    posterior = list(alpha = alpha_post, beta = beta_post),
    posterior_mean = post_mean,
    posterior_variance = post_var,
    posterior_sd = sqrt(post_var),
    hdi_95 = c(lower = hdi_lower, upper = hdi_upper),
    map_estimate = (alpha_post - 1) / (alpha_post + beta_post - 2)
  )
}

# ---- Linear Regression (Manual OLS) ----

#' Ordinary Least Squares regression computed manually.
#' Beta = (X'X)^(-1) X'y
#' @param X Design matrix (n × p), include intercept column if desired
#' @param y Response vector (n × 1)
#' @return Named list with coefficients, residuals, R-squared, diagnostics
omni_ols_regression <- function(X, y) {
  stopifnot(is.matrix(X), is.numeric(y))
  stopifnot(nrow(X) == length(y))
  
  n <- nrow(X)
  p <- ncol(X)
  
  # Normal equations: Beta = solve(t(X) %*% X) %*% t(X) %*% y
  XtX <- crossprod(X)           # t(X) %*% X  (p × p)
  Xty <- crossprod(X, y)        # t(X) %*% y  (p × 1)
  beta <- solve(XtX, Xty)       # (X'X)^{-1} X'y
  
  # Fitted values and residuals
  y_hat <- X %*% beta
  residuals <- y - y_hat
  
  # Sum of squares
  ss_res <- sum(residuals^2)
  ss_tot <- sum((y - mean(y))^2)
  r_squared <- 1 - ss_res / ss_tot
  adj_r_squared <- 1 - (1 - r_squared) * (n - 1) / (n - p - 1)
  
  # Standard errors
  mse <- ss_res / (n - p)
  var_beta <- mse * solve(XtX)
  se_beta <- sqrt(diag(var_beta))
  
  # t-statistics and p-values for each coefficient
  t_stats <- as.vector(beta) / se_beta
  p_values <- 2 * pt(-abs(t_stats), df = n - p)
  
  list(
    method = "OLS Linear Regression",
    coefficients = as.vector(beta),
    standard_errors = se_beta,
    t_statistics = t_stats,
    p_values = p_values,
    r_squared = r_squared,
    adj_r_squared = adj_r_squared,
    residual_se = sqrt(mse),
    n = n,
    p = p,
    degrees_of_freedom = n - p
  )
}

# ---- Bootstrap Confidence Interval ----

#' Non-parametric bootstrap confidence interval for a statistic.
#' @param x Numeric vector
#' @param stat_fn Function that computes the statistic (default: mean)
#' @param n_boot Number of bootstrap replicates (default: 10000)
#' @param conf_level Confidence level (default: 0.95)
#' @return Named list with bootstrap CI and distribution summary
omni_bootstrap_ci <- function(x, stat_fn = mean, n_boot = 10000,
                               conf_level = 0.95) {
  stopifnot(is.numeric(x), length(x) > 1)
  
  n <- length(x)
  boot_stats <- numeric(n_boot)
  
  set.seed(42)  # Reproducibility
  for (b in seq_len(n_boot)) {
    boot_sample <- sample(x, size = n, replace = TRUE)
    boot_stats[b] <- stat_fn(boot_sample)
  }
  
  alpha <- 1 - conf_level
  ci <- quantile(boot_stats, probs = c(alpha / 2, 1 - alpha / 2))
  
  list(
    method = "Non-Parametric Bootstrap",
    observed_statistic = stat_fn(x),
    n_bootstrap = n_boot,
    confidence_level = conf_level,
    ci_lower = unname(ci[1]),
    ci_upper = unname(ci[2]),
    bootstrap_mean = mean(boot_stats),
    bootstrap_sd = sd(boot_stats),
    bias = mean(boot_stats) - stat_fn(x)
  )
}

# ---- Diagnostics ----

#' OMNI Engine Registry diagnostics.
omni_statistical_inference_diagnostics <- function() {
  list(
    engine = "OmniStatisticalInferenceEngine",
    layer = "R Compute",
    capabilities = c(
      "descriptive_statistics",
      "welch_t_test",
      "bayesian_beta_binomial",
      "ols_regression",
      "bootstrap_ci"
    ),
    learned_logic = c(
      "vectorized-column-operations",
      "welch-satterthwaite-df",
      "beta-binomial-conjugate-prior",
      "normal-equations-ols",
      "bootstrap-percentile-ci",
      "fishers-skewness-kurtosis",
      "crossprod-efficient-matrix-multiply"
    )
  )
}
