# Omni ChemLLMBench Stats (R)
omni_chem_accuracy <- function(preds, golds) {
  correct <- sum(preds == golds)
  round(correct / max(length(golds), 1), 4)
}
omni_property_mae <- function(preds, golds) {
  round(mean(abs(preds - golds)), 4)
}
omni_reaction_eval <- function(pred_products, gold_products) {
  exact <- sum(pred_products == gold_products)
  list(exact_match = round(exact / max(length(gold_products), 1), 4))
}
