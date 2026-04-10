# omni-cloudflare-r2 â€” R Statistical Analysis Module

omni_cloudflare_r2_summary <- function(data) { list(mean=mean(data), median=median(data), sd=sd(data), var=var(data), min=min(data), max=max(data), q25=quantile(data, 0.25), q75=quantile(data, 0.75), n=length(data)) }
omni_cloudflare_r2_correlation <- function(x, y) { cor(x, y) }
omni_cloudflare_r2_regression <- function(x, y) { model <- lm(y ~ x); list(intercept=coef(model)[1], slope=coef(model)[2], r_squared=summary(model)\.squared) }
omni_cloudflare_r2_t_test <- function(x, y) { result <- t.test(x, y); list(statistic=result\, p_value=result\.value, ci_lower=result\.int[1], ci_upper=result\.int[2]) }
omni_cloudflare_r2_chi_squared <- function(observed, expected) { result <- chisq.test(observed, p=expected/sum(expected)); list(statistic=result\, p_value=result\.value) }
omni_cloudflare_r2_normalize <- function(x) { (x - min(x)) / (max(x) - min(x)) }
omni_cloudflare_r2_z_score <- function(x) { (x - mean(x)) / sd(x) }