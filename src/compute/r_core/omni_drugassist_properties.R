# Omni DrugAssist Property Calculator (R)
# Compute Layer: Molecular property computation for drug discovery.
# Ref: blazerye/DrugAssist
omni_logp_estimate <- function(smiles) {
  n_c <- nchar(gsub("[^Cc]", "", smiles))
  n_o <- nchar(gsub("[^Oo]", "", smiles))
  n_n <- nchar(gsub("[^Nn]", "", smiles))
  logp <- 0.5 * n_c - 1.0 * n_o - 0.5 * n_n
  list(smiles = smiles, estimated_logp = round(logp, 4), atoms = n_c + n_o + n_n)
}
omni_drug_likeness <- function(mw, logp, hbd, hba) {
  violations <- sum(c(mw > 500, logp > 5, hbd > 5, hba > 10))
  list(passes = violations <= 1, violations = violations)
}
