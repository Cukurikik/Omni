# omni_statistical_analysis.R — Statistical Analysis for Model Evaluation
# Inspired by: A/B testing + Bio-NER evaluation statistics
# Layer: Compute / R
#
# Statistical significance testing, confidence intervals,
# and effect size computation for ML model comparison.

library(methods)

#' Compute Welch's t-test for model comparison
#' @param scores_a Numeric vector of model A scores
#' @param scores_b Numeric vector of model B scores
#' @param alpha Significance level (default 0.05)
#' @return List with test statistics, p-value, and decision
omni_welch_test <- function(scores_a, scores_b, alpha = 0.05) {
  n_a <- length(scores_a)
  n_b <- length(scores_b)
  
  mean_a <- mean(scores_a)
  mean_b <- mean(scores_b)
  var_a <- var(scores_a)
  var_b <- var(scores_b)
  
  se <- sqrt(var_a / n_a + var_b / n_b)
  t_stat <- (mean_a - mean_b) / se
  
  # Welch-Satterthwaite degrees of freedom
  df <- (var_a / n_a + var_b / n_b)^2 / (
    (var_a / n_a)^2 / (n_a - 1) + (var_b / n_b)^2 / (n_b - 1)
  )
  
  p_value <- 2 * pt(-abs(t_stat), df)
  
  list(
    mean_a = mean_a,
    mean_b = mean_b,
    difference = mean_a - mean_b,
    t_statistic = t_stat,
    degrees_of_freedom = df,
    p_value = p_value,
    significant = p_value < alpha,
    alpha = alpha,
    winner = ifelse(p_value < alpha,
                    ifelse(mean_a > mean_b, "model_a", "model_b"),
                    "no_significant_difference")
  )
}

#' Compute Cohen's d effect size
#' @param scores_a Numeric vector of model A scores
#' @param scores_b Numeric vector of model B scores
#' @return List with effect size and interpretation
omni_cohens_d <- function(scores_a, scores_b) {
  n_a <- length(scores_a)
  n_b <- length(scores_b)
  
  mean_diff <- mean(scores_a) - mean(scores_b)
  pooled_sd <- sqrt(((n_a - 1) * var(scores_a) + (n_b - 1) * var(scores_b)) /
                      (n_a + n_b - 2))
  
  d <- mean_diff / pooled_sd
  
  interpretation <- if (abs(d) < 0.2) "negligible"
  else if (abs(d) < 0.5) "small"
  else if (abs(d) < 0.8) "medium"
  else "large"
  
  list(
    cohens_d = d,
    interpretation = interpretation,
    pooled_sd = pooled_sd,
    mean_difference = mean_diff
  )
}

#' Bootstrap confidence interval for a metric
#' @param scores Numeric vector of scores
#' @param n_bootstrap Number of bootstrap iterations
#' @param confidence Confidence level (default 0.95)
#' @param stat_fn Function to compute statistic (default: mean)
#' @return List with CI bounds and point estimate
omni_bootstrap_ci <- function(scores, n_bootstrap = 10000,
                               confidence = 0.95, stat_fn = mean) {
  n <- length(scores)
  bootstrap_stats <- numeric(n_bootstrap)
  
  set.seed(42)  # Reproducibility
  for (i in seq_len(n_bootstrap)) {
    sample_idx <- sample.int(n, n, replace = TRUE)
    bootstrap_stats[i] <- stat_fn(scores[sample_idx])
  }
  
  alpha <- 1 - confidence
  lower <- quantile(bootstrap_stats, alpha / 2)
  upper <- quantile(bootstrap_stats, 1 - alpha / 2)
  
  list(
    point_estimate = stat_fn(scores),
    ci_lower = as.numeric(lower),
    ci_upper = as.numeric(upper),
    confidence = confidence,
    std_error = sd(bootstrap_stats),
    n_bootstrap = n_bootstrap
  )
}

#' Compute precision, recall, F1 with confidence intervals
#' @param true_labels Vector of true labels
#' @param pred_labels Vector of predicted labels
#' @param positive_class Label for positive class
#' @return List with metrics and bootstrap CIs
omni_classification_metrics <- function(true_labels, pred_labels,
                                         positive_class = 1) {
  tp <- sum(pred_labels == positive_class & true_labels == positive_class)
  fp <- sum(pred_labels == positive_class & true_labels != positive_class)
  fn <- sum(pred_labels != positive_class & true_labels == positive_class)
  tn <- sum(pred_labels != positive_class & true_labels != positive_class)
  
  precision <- if (tp + fp > 0) tp / (tp + fp) else 0
  recall <- if (tp + fn > 0) tp / (tp + fn) else 0
  f1 <- if (precision + recall > 0) 2 * precision * recall / (precision + recall) else 0
  accuracy <- (tp + tn) / (tp + fp + fn + tn)
  
  # Bootstrap CI for F1
  n <- length(true_labels)
  f1_bootstrap <- function(indices) {
    tl <- true_labels[indices]
    pl <- pred_labels[indices]
    tp_b <- sum(pl == positive_class & tl == positive_class)
    fp_b <- sum(pl == positive_class & tl != positive_class)
    fn_b <- sum(pl != positive_class & tl == positive_class)
    p <- if (tp_b + fp_b > 0) tp_b / (tp_b + fp_b) else 0
    r <- if (tp_b + fn_b > 0) tp_b / (tp_b + fn_b) else 0
    if (p + r > 0) 2 * p * r / (p + r) else 0
  }
  
  f1_ci <- omni_bootstrap_ci(seq_len(n), stat_fn = f1_bootstrap)
  
  list(
    precision = precision,
    recall = recall,
    f1_score = f1,
    accuracy = accuracy,
    tp = tp, fp = fp, fn = fn, tn = tn,
    f1_ci_lower = f1_ci$ci_lower,
    f1_ci_upper = f1_ci$ci_upper,
    support = tp + fn
  )
}

#' McNemar's test for paired model comparison
#' @param model_a_correct Logical vector: model A correct predictions
#' @param model_b_correct Logical vector: model B correct predictions
#' @return List with chi-squared statistic and p-value
omni_mcnemar_test <- function(model_a_correct, model_b_correct) {
  # Count discordant pairs
  b <- sum(model_a_correct & !model_b_correct)  # A right, B wrong
  c <- sum(!model_a_correct & model_b_correct)   # A wrong, B right
  
  if (b + c == 0) {
    return(list(
      chi_squared = 0,
      p_value = 1.0,
      significant = FALSE,
      b = b, c = c,
      message = "Models have identical predictions on all samples"
    ))
  }
  
  # McNemar's test with continuity correction
  chi_sq <- (abs(b - c) - 1)^2 / (b + c)
  p_value <- pchisq(chi_sq, df = 1, lower.tail = FALSE)
  
  list(
    chi_squared = chi_sq,
    p_value = p_value,
    significant = p_value < 0.05,
    b = b,
    c = c,
    better_model = ifelse(b > c, "model_a", "model_b")
  )
}

#' Generate comprehensive model comparison report
#' @param scores_a Numeric vector of model A scores
#' @param scores_b Numeric vector of model B scores
#' @param model_a_name Name for model A
#' @param model_b_name Name for model B
#' @return List with full comparison results
omni_model_comparison_report <- function(scores_a, scores_b,
                                          model_a_name = "Model A",
                                          model_b_name = "Model B") {
  ttest <- omni_welch_test(scores_a, scores_b)
  effect <- omni_cohens_d(scores_a, scores_b)
  ci_a <- omni_bootstrap_ci(scores_a)
  ci_b <- omni_bootstrap_ci(scores_b)
  
  list(
    models = c(model_a_name, model_b_name),
    summary = list(
      mean_a = mean(scores_a),
      mean_b = mean(scores_b),
      sd_a = sd(scores_a),
      sd_b = sd(scores_b),
      n_a = length(scores_a),
      n_b = length(scores_b)
    ),
    welch_test = ttest,
    effect_size = effect,
    confidence_intervals = list(
      model_a = ci_a,
      model_b = ci_b
    ),
    recommendation = ifelse(
      ttest$significant,
      paste(ttest$winner, "is significantly better with",
            effect$interpretation, "effect size"),
      "No statistically significant difference between models"
    )
  )
}
