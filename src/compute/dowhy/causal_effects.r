# Omni Causal Effects (DoWhy Integration)

estimate_propensity_score <- function(data, treatment, covariates) {
  form <- as.formula(paste(treatment, "~", paste(covariates, collapse="+")))
  model <- glm(form, data=data, family=binomial())
  return(predict(model, type="response"))
}

# Example use:
# ps <- estimate_propensity_score(df, "T", c("C1", "C2"))
