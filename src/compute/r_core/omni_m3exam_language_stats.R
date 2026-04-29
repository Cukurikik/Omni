# Omni M3Exam Language Stats (R)
# Ref: DAMO-NLP-SG/M3Exam
omni_m3exam_accuracy <- function(predictions, answers) {
  correct <- sum(toupper(trimws(predictions)) == toupper(trimws(answers)))
  list(accuracy = correct / max(length(answers), 1), n = length(answers), correct = correct)
}
omni_by_language <- function(df) {
  tapply(df$correct, df$language, function(x) mean(x, na.rm = TRUE))
}
omni_by_level <- function(df) {
  tapply(df$correct, df$level, function(x) mean(x, na.rm = TRUE))
}
