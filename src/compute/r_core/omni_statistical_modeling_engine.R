# ===========================================================================
# OMNI STATISTICAL MODELING ENGINE (SEMESTER 3 — BATCH 38.6)
# ===========================================================================
# Absorbed From  : R stats package + lm() + glm() + ggplot2 themes
# Logic Inherited: R / Compute Layer (Linear Models & Statistical Inference)
# ===========================================================================
#
# By studying R's stats package, Mother learned:
#   1. lm() fits linear models via QR decomposition
#   2. summary() provides coefficients, std errors, t-statistics, p-values
#   3. Formula interface (y ~ x1 + x2) describes model structure
#   4. ANOVA decomposes variance into model vs residual
#   5. Diagnostic plots (residuals, QQ, leverage) validate assumptions

# ============================================================
# PART 1: Linear Regression Engine
# ============================================================

#' Fit a linear model using QR decomposition.
#'
#' @param formula A formula (e.g., y ~ x1 + x2)
#' @param data A data.frame
#' @return An OmniLinearModel object
omni_lm <- function(formula, data) {
  # Parse formula
  mf <- model.frame(formula, data)
  y <- model.response(mf)
  X <- model.matrix(formula, data)

  n <- nrow(X)
  p <- ncol(X)

  # QR decomposition for numerical stability
  qr_decomp <- qr(X)
  coefficients <- qr.coef(qr_decomp, y)

  # Fitted values and residuals
  fitted_values <- X %*% coefficients
  residuals <- y - fitted_values

  # Degrees of freedom
  df_model <- p - 1
  df_residual <- n - p
  df_total <- n - 1

  # Sum of squares
  ss_total <- sum((y - mean(y))^2)
  ss_residual <- sum(residuals^2)
  ss_model <- ss_total - ss_residual

  # R-squared and adjusted R-squared
  r_squared <- 1 - ss_residual / ss_total
  adj_r_squared <- 1 - (1 - r_squared) * df_total / df_residual

  # Residual standard error
  rse <- sqrt(ss_residual / df_residual)

  # Standard errors of coefficients
  # Var(beta) = sigma^2 * (X'X)^{-1}
  XtX_inv <- chol2inv(qr.R(qr_decomp))
  se <- sqrt(diag(XtX_inv) * (ss_residual / df_residual))

  # t-statistics and p-values
  t_values <- coefficients / se
  p_values <- 2 * pt(abs(t_values), df_residual, lower.tail = FALSE)

  # F-statistic
  ms_model <- ss_model / df_model
  ms_residual <- ss_residual / df_residual
  f_statistic <- ms_model / ms_residual
  f_p_value <- pf(f_statistic, df_model, df_residual, lower.tail = FALSE)

  # AIC and BIC
  log_likelihood <- -n/2 * (log(2 * pi) + log(ss_residual / n) + 1)
  aic <- -2 * log_likelihood + 2 * p
  bic <- -2 * log_likelihood + log(n) * p

  # Build result object
  result <- list(
    coefficients = coefficients,
    se = se,
    t_values = t_values,
    p_values = p_values,
    residuals = as.vector(residuals),
    fitted_values = as.vector(fitted_values),
    r_squared = r_squared,
    adj_r_squared = adj_r_squared,
    rse = rse,
    f_statistic = f_statistic,
    f_p_value = f_p_value,
    df_model = df_model,
    df_residual = df_residual,
    ss_total = ss_total,
    ss_model = ss_model,
    ss_residual = ss_residual,
    aic = aic,
    bic = bic,
    log_likelihood = log_likelihood,
    n = n,
    p = p,
    formula = formula,
    qr = qr_decomp,
    call = match.call()
  )

  class(result) <- "OmniLinearModel"
  return(result)
}

#' Summary method for OmniLinearModel
summary.OmniLinearModel <- function(object, ...) {
  cat("\nOmni Linear Model\n")
  cat("==================\n\n")
  cat("Call:\n")
  print(object$call)
  cat("\n")

  # Coefficients table
  coef_table <- data.frame(
    Estimate = object$coefficients,
    Std.Error = object$se,
    t.value = object$t_values,
    Pr = object$p_values
  )

  # Significance stars
  coef_table$Sig <- ifelse(
    coef_table$Pr < 0.001, "***",
    ifelse(coef_table$Pr < 0.01, "**",
    ifelse(coef_table$Pr < 0.05, "*",
    ifelse(coef_table$Pr < 0.1, ".", " ")))
  )

  cat("Coefficients:\n")
  print(coef_table, digits = 4)

  cat("\n---\n")
  cat("Signif. codes: 0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1\n\n")

  cat(sprintf("Residual standard error: %.4f on %d degrees of freedom\n",
              object$rse, object$df_residual))
  cat(sprintf("Multiple R-squared: %.4f, Adjusted R-squared: %.4f\n",
              object$r_squared, object$adj_r_squared))
  cat(sprintf("F-statistic: %.2f on %d and %d DF, p-value: %.4e\n",
              object$f_statistic, object$df_model, object$df_residual, object$f_p_value))
  cat(sprintf("AIC: %.2f, BIC: %.2f\n", object$aic, object$bic))

  invisible(object)
}

#' Predict method for OmniLinearModel
predict.OmniLinearModel <- function(object, newdata = NULL, interval = "none",
                                     level = 0.95, ...) {
  if (is.null(newdata)) {
    return(object$fitted_values)
  }

  X_new <- model.matrix(object$formula, newdata)
  predictions <- X_new %*% object$coefficients

  if (interval == "confidence" || interval == "prediction") {
    XtX_inv <- chol2inv(qr.R(object$qr))
    se_fit <- sqrt(rowSums((X_new %*% XtX_inv) * X_new) * object$rse^2)

    alpha <- 1 - level
    t_crit <- qt(1 - alpha / 2, object$df_residual)

    if (interval == "prediction") {
      se_pred <- sqrt(se_fit^2 + object$rse^2)
      return(data.frame(
        fit = as.vector(predictions),
        lwr = as.vector(predictions - t_crit * se_pred),
        upr = as.vector(predictions + t_crit * se_pred)
      ))
    } else {
      return(data.frame(
        fit = as.vector(predictions),
        lwr = as.vector(predictions - t_crit * se_fit),
        upr = as.vector(predictions + t_crit * se_fit)
      ))
    }
  }

  return(as.vector(predictions))
}

# ============================================================
# PART 2: ANOVA
# ============================================================

#' Perform ANOVA on an OmniLinearModel
omni_anova <- function(model) {
  anova_table <- data.frame(
    Df = c(model$df_model, model$df_residual),
    Sum.Sq = c(model$ss_model, model$ss_residual),
    Mean.Sq = c(model$ss_model / model$df_model,
                 model$ss_residual / model$df_residual),
    F.value = c(model$f_statistic, NA),
    Pr.F = c(model$f_p_value, NA),
    row.names = c("Model", "Residuals")
  )

  class(anova_table) <- c("OmniAnova", "data.frame")
  return(anova_table)
}

# ============================================================
# PART 3: Diagnostic Plots Data
# ============================================================

#' Generate diagnostic data for model validation
omni_diagnostics_data <- function(model) {
  standardized_residuals <- model$residuals / model$rse

  # Cook's distance
  h <- hatvalues_from_qr(model$qr)
  cooks_d <- (standardized_residuals^2 * h) / (model$p * (1 - h)^2)

  list(
    residuals = model$residuals,
    standardized_residuals = standardized_residuals,
    fitted_values = model$fitted_values,
    qq_theoretical = qnorm(ppoints(length(model$residuals))),
    qq_sample = sort(standardized_residuals),
    leverage = h,
    cooks_distance = cooks_d
  )
}

#' Helper: extract hat values from QR decomposition
hatvalues_from_qr <- function(qr_obj) {
  Q <- qr.Q(qr_obj)
  rowSums(Q^2)
}

# ============================================================
# PART 4: Hypothesis Testing
# ============================================================

#' Two-sample t-test
omni_t_test <- function(x, y = NULL, mu = 0, alternative = "two.sided",
                         paired = FALSE, var.equal = FALSE) {
  if (is.null(y)) {
    # One-sample t-test
    n <- length(x)
    t_stat <- (mean(x) - mu) / (sd(x) / sqrt(n))
    df <- n - 1
  } else if (paired) {
    d <- x - y
    n <- length(d)
    t_stat <- mean(d) / (sd(d) / sqrt(n))
    df <- n - 1
  } else if (var.equal) {
    nx <- length(x)
    ny <- length(y)
    sp <- sqrt(((nx-1)*var(x) + (ny-1)*var(y)) / (nx + ny - 2))
    t_stat <- (mean(x) - mean(y)) / (sp * sqrt(1/nx + 1/ny))
    df <- nx + ny - 2
  } else {
    # Welch's t-test
    nx <- length(x)
    ny <- length(y)
    vx <- var(x) / nx
    vy <- var(y) / ny
    t_stat <- (mean(x) - mean(y)) / sqrt(vx + vy)
    df <- (vx + vy)^2 / (vx^2/(nx-1) + vy^2/(ny-1))
  }

  p_value <- switch(alternative,
    "two.sided" = 2 * pt(abs(t_stat), df, lower.tail = FALSE),
    "less"      = pt(t_stat, df),
    "greater"   = pt(t_stat, df, lower.tail = FALSE)
  )

  list(
    statistic = t_stat,
    df = df,
    p_value = p_value,
    alternative = alternative,
    method = ifelse(is.null(y), "One Sample t-test",
             ifelse(paired, "Paired t-test",
             ifelse(var.equal, "Two Sample t-test", "Welch Two Sample t-test")))
  )
}

# ============================================================
# Engine Diagnostics
# ============================================================

omni_engine_diagnostics <- function() {
  list(
    engine = "OmniStatisticalModelingEngine",
    layer = "R Compute",
    capabilities = c(
      "omni_lm (linear regression)",
      "omni_anova (analysis of variance)",
      "omni_t_test (t-test family)",
      "predict with intervals",
      "diagnostic plots data"
    ),
    learned_logic = c(
      "qr-decomposition-numerical-stability",
      "ols-normal-equations-chol2inv",
      "t-statistic-p-value-significance",
      "f-statistic-model-overall",
      "aic-bic-model-selection",
      "cooks-distance-influence",
      "welch-t-test-unequal-variance",
      "confidence-prediction-intervals"
    )
  )
}
