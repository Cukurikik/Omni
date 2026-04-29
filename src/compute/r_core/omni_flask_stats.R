# Omni FLASK Statistical Evaluator (R)
# Ref: kaistAI/FLASK — ICLR 2024
omni_flask_skill_stats <- function(scores_matrix) {
  skills <- colnames(scores_matrix)
  means <- colMeans(scores_matrix, na.rm = TRUE)
  sds <- apply(scores_matrix, 2, sd, na.rm = TRUE)
  data.frame(skill = skills, mean = round(means, 4), sd = round(sds, 4))
}

omni_flask_correlation <- function(skill_a, skill_b) {
  r <- cor(skill_a, skill_b, use = "complete.obs")
  round(r, 4)
}

omni_flask_inter_annotator <- function(annotator1, annotator2) {
  agreement <- sum(annotator1 == annotator2, na.rm = TRUE)
  total <- sum(!is.na(annotator1) & !is.na(annotator2))
  round(agreement / max(total, 1), 4)
}
