# OMNI Compute Layer — R Statistical Analysis for Model Evaluation
# Production model evaluation with statistical significance testing.

library(dplyr)
library(tidyr)

#' Compute comprehensive classification metrics
#' @param predictions Predicted labels
#' @param actuals Actual labels
#' @return Named list of metrics
omni_classification_metrics <- function(predictions, actuals) {
  stopifnot(length(predictions) == length(actuals))
  
  classes <- unique(c(predictions, actuals))
  n <- length(predictions)
  
  # Per-class precision, recall, F1
  per_class <- lapply(classes, function(cls) {
    tp <- sum(predictions == cls & actuals == cls)
    fp <- sum(predictions == cls & actuals != cls)
    fn <- sum(predictions != cls & actuals == cls)
    
    precision <- ifelse(tp + fp > 0, tp / (tp + fp), 0)
    recall <- ifelse(tp + fn > 0, tp / (tp + fn), 0)
    f1 <- ifelse(precision + recall > 0, 2 * precision * recall / (precision + recall), 0)
    
    list(class = cls, precision = precision, recall = recall, f1 = f1, support = sum(actuals == cls))
  })
  
  # Macro and weighted averages
  macro_f1 <- mean(sapply(per_class, function(x) x$f1))
  weights <- sapply(per_class, function(x) x$support) / n
  weighted_f1 <- sum(sapply(per_class, function(x) x$f1) * weights)
  accuracy <- sum(predictions == actuals) / n
  
  list(
    accuracy = accuracy,
    macro_f1 = macro_f1,
    weighted_f1 = weighted_f1,
    per_class = per_class,
    confusion_matrix = table(Predicted = predictions, Actual = actuals)
  )
}

#' McNemar's test for comparing two models
#' @param model_a_correct Logical vector of model A correctness
#' @param model_b_correct Logical vector of model B correctness
#' @return Test result
omni_mcnemar_test <- function(model_a_correct, model_b_correct) {
  contingency <- table(
    ModelA = model_a_correct,
    ModelB = model_b_correct
  )
  
  b <- contingency["TRUE", "FALSE"]  # A correct, B wrong
  c_val <- contingency["FALSE", "TRUE"]  # A wrong, B correct
  
  statistic <- (abs(b - c_val) - 1)^2 / (b + c_val)
  p_value <- 1 - pchisq(statistic, df = 1)
  
  list(
    statistic = statistic,
    p_value = p_value,
    significant = p_value < 0.05,
    a_better_count = b,
    b_better_count = c_val
  )
}

#' Bootstrap confidence interval for a metric
#' @param data Numeric vector
#' @param metric_fn Function to compute metric
#' @param n_boot Number of bootstrap samples
#' @param alpha Significance level
omni_bootstrap_ci <- function(data, metric_fn, n_boot = 1000, alpha = 0.05) {
  boot_values <- replicate(n_boot, {
    idx <- sample(length(data), replace = TRUE)
    metric_fn(data[idx])
  })
  
  list(
    estimate = metric_fn(data),
    ci_lower = quantile(boot_values, alpha / 2),
    ci_upper = quantile(boot_values, 1 - alpha / 2),
    std_error = sd(boot_values)
  )
}

#' Compute perplexity from log probabilities
#' @param log_probs Vector of log probabilities
omni_perplexity <- function(log_probs) {
  exp(-mean(log_probs))
}

#' A/B test analysis for model comparison
#' @param metric_a Metric values for model A
#' @param metric_b Metric values for model B
omni_ab_test <- function(metric_a, metric_b) {
  t_result <- t.test(metric_a, metric_b, paired = TRUE)
  effect_size <- (mean(metric_a) - mean(metric_b)) / sd(metric_a - metric_b)
  
  list(
    mean_a = mean(metric_a),
    mean_b = mean(metric_b),
    difference = mean(metric_a) - mean(metric_b),
    t_statistic = t_result$statistic,
    p_value = t_result$p.value,
    significant = t_result$p.value < 0.05,
    cohens_d = effect_size,
    ci = t_result$conf.int
  )
}
