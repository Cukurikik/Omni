omni_propensity_score_matching <- function(treatment, covariates) {
  # Logistic regression for propensity score
  model <- glm(treatment ~ ., family = binomial(link = "logit"), data = covariates)
  scores <- predict(model, type = "response")
  return(scores)
}

omni_calculate_ate <- function(outcome, treatment, scores) {
  treated_mean <- mean(outcome[treatment == 1] / scores[treatment == 1])
  control_mean <- mean(outcome[treatment == 0] / (1 - scores[treatment == 0]))
  return(treated_mean - control_mean)
}
