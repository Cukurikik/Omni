OmniResult <- setClass(
  "OmniResult",
  slots = c(
    value = "ANY",
    error = "character",
    is_ok = "logical"
  )
)

calculate_rlhf_reward <- function(human_scores, model_outputs) {
  if (length(human_scores) != length(model_outputs)) {
    return(OmniResult(value=NULL, error="Lengths do not match", is_ok=FALSE))
  }
  
  if (length(human_scores) == 0) {
    return(OmniResult(value=NULL, error="Empty input arrays", is_ok=FALSE))
  }
  
  # Bradley-Terry model alignment calculation
  reward_score <- 0.0
  n <- length(human_scores)
  
  for (i in 1:n) {
      # Math: reward shaping based on human variance
      variance_penalty <- (human_scores[i] - mean(human_scores))^2
      reward_score <- reward_score + (human_scores[i] * 0.8 - variance_penalty * 0.2)
  }
  
  reward_score <- reward_score / n
  
  return(OmniResult(value=reward_score, error="", is_ok=TRUE))
}
