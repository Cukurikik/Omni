# OMNI MOTHER — SEMESTER 13 REMEDIATION
# R Language — Computational & Data Layer (OMNI Zero-Mock Implementation)
# Implements deterministic statistical hypothesis testing with exact p-value computation.
# Absorbs patterns from: R base::stats, t.test, wilcox.test

#' Monadic Result container for R computations.
#' @param value Result value (NULL on error)
#' @param is_ok Logical success flag
#' @param error Error message (empty string on success)
omni_result <- function(value = NULL, is_ok = TRUE, error = "") {
  list(value = value, is_ok = is_ok, error = error)
}

#' Welch's Two-Sample t-test (unequal variances).
#' Computes t-statistic and degrees of freedom using Welch-Satterthwaite equation.
#'
#' @param x Numeric vector — sample 1
#' @param y Numeric vector — sample 2
#' @param alpha Significance level (default 0.05)
#' @return List with t_statistic, df, p_value, reject_null, ci_lower, ci_upper
#' @export
omni_welch_t_test <- function(x, y, alpha = 0.05) {
  if (!is.numeric(x) || !is.numeric(y)) {
    return(omni_result(is_ok = FALSE, error = "R t-test requires numeric input vectors."))
  }
  if (length(x) < 2 || length(y) < 2) {
    return(omni_result(is_ok = FALSE, error = "R t-test requires at least 2 observations per group."))
  }
  if (alpha <= 0 || alpha >= 1) {
    return(omni_result(is_ok = FALSE, error = "Significance level alpha must be in (0, 1)."))
  }

  n1 <- length(x)
  n2 <- length(y)
  mean1 <- mean(x)
  mean2 <- mean(y)
  var1 <- var(x)
  var2 <- var(y)

  if (var1 == 0 && var2 == 0) {
    return(omni_result(is_ok = FALSE, error = "Both samples have zero variance — t-test undefined."))
  }

  # Welch's t-statistic
  se <- sqrt(var1 / n1 + var2 / n2)
  t_stat <- (mean1 - mean2) / se

  # Welch-Satterthwaite degrees of freedom
  num <- (var1 / n1 + var2 / n2)^2
  denom <- (var1 / n1)^2 / (n1 - 1) + (var2 / n2)^2 / (n2 - 1)
  df <- num / denom

  # Two-tailed p-value
  p_value <- 2 * pt(-abs(t_stat), df = df)

  # Confidence interval for difference of means
  t_crit <- qt(1 - alpha / 2, df = df)
  ci_lower <- (mean1 - mean2) - t_crit * se
  ci_upper <- (mean1 - mean2) + t_crit * se

  result <- list(
    t_statistic = t_stat,
    degrees_of_freedom = df,
    p_value = p_value,
    reject_null = p_value < alpha,
    ci_lower = ci_lower,
    ci_upper = ci_upper,
    mean_difference = mean1 - mean2,
    effect_size_cohens_d = (mean1 - mean2) / sqrt((var1 + var2) / 2),
    alpha = alpha
  )

  return(omni_result(value = result))
}

#' One-way ANOVA F-test for comparing multiple group means.
#'
#' @param groups List of numeric vectors (one per group)
#' @param alpha Significance level (default 0.05)
#' @return List with f_statistic, df_between, df_within, p_value, reject_null
#' @export
omni_one_way_anova <- function(groups, alpha = 0.05) {
  if (!is.list(groups) || length(groups) < 2) {
    return(omni_result(is_ok = FALSE, error = "ANOVA requires a list of at least 2 groups."))
  }

  k <- length(groups)
  ns <- sapply(groups, length)
  N <- sum(ns)

  if (any(ns < 2)) {
    return(omni_result(is_ok = FALSE, error = "Each ANOVA group must have >= 2 observations."))
  }

  group_means <- sapply(groups, mean)
  grand_mean <- mean(unlist(groups))

  # Sum of Squares Between
  ss_between <- sum(ns * (group_means - grand_mean)^2)
  df_between <- k - 1

  # Sum of Squares Within
  ss_within <- sum(sapply(seq_along(groups), function(i) {
    sum((groups[[i]] - group_means[i])^2)
  }))
  df_within <- N - k

  # Mean Squares
  ms_between <- ss_between / df_between
  ms_within <- ss_within / df_within

  if (ms_within == 0) {
    return(omni_result(is_ok = FALSE, error = "Within-group variance is zero — F-test undefined."))
  }

  f_stat <- ms_between / ms_within
  p_value <- pf(f_stat, df_between, df_within, lower.tail = FALSE)

  result <- list(
    f_statistic = f_stat,
    df_between = df_between,
    df_within = df_within,
    p_value = p_value,
    reject_null = p_value < alpha,
    ss_between = ss_between,
    ss_within = ss_within,
    eta_squared = ss_between / (ss_between + ss_within)
  )

  return(omni_result(value = result))
}
