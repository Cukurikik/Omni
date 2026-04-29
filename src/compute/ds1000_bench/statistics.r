suppressMessages(library(dplyr))

calculate_metrics <- function(df) {
  if (nrow(df) == 0) stop("Dataframe is empty")
  df %>% summarise(mean_score = mean(score, na.rm = TRUE), pass_rate = sum(passed)/n())
}
