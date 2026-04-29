# Omni LQAE Codebook Stats (R)
# Ref: haoliuhl/language-quantized-autoencoders
omni_codebook_usage <- function(indices, codebook_size) {
  counts <- tabulate(indices + 1, nbins = codebook_size)
  list(usage_rate = sum(counts > 0) / codebook_size,
       entropy = -sum(ifelse(counts > 0, (counts/sum(counts)) * log2(counts/sum(counts)), 0)))
}
omni_commitment_loss <- function(z_e, z_q) {
  mean((z_e - z_q)^2)
}
