# OMNI Framework - R Statistical Analysis for CommonLit Readability
# Implements regression analysis and descriptive statistics for readability metrics

library(stats)
library(dplyr)

calculate_readability_stats <- function(readability_scores, target_scores) {
  # Create a data frame
  df <- data.frame(
    predicted = readability_scores,
    actual = target_scores
  )
  
  # Calculate Root Mean Square Error (RMSE)
  rmse <- sqrt(mean((df$predicted - df$actual)^2))
  
  # Calculate Pearson Correlation
  correlation <- cor(df$predicted, df$actual, method = "pearson")
  
  # Fit a linear model for bias detection
  model <- lm(actual ~ predicted, data = df)
  summary_model <- summary(model)
  
  result <- list(
    RMSE = rmse,
    Pearson_Correlation = correlation,
    R_Squared = summary_model$r.squared,
    P_Value = coef(summary_model)[2,4]
  )
  
  return(result)
}

# Example Usage
# stats <- calculate_readability_stats(c(1.2, -0.5, 0.8), c(1.0, -0.4, 0.9))
# print(stats)
