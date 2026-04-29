/* Omni AlphaRec Contrastive Loss Kernel (C) */
/* Ref: LehengTHU/AlphaRec — ICLR 2025 Oral */
#include <math.h>
double omni_cosine_sim(const double* a, const double* b, int d) {
    double dot = 0, na = 0, nb = 0;
    for (int i = 0; i < d; i++) { dot += a[i]*b[i]; na += a[i]*a[i]; nb += b[i]*b[i]; }
    double denom = sqrt(na) * sqrt(nb);
    return denom > 1e-9 ? dot / denom : 0;
}
double omni_contrastive_loss(const double* anchor, const double* pos, const double** negs,
                              int n_neg, int d, double temp) {
    double pos_score = exp(omni_cosine_sim(anchor, pos, d) / temp);
    double neg_sum = 0;
    for (int i = 0; i < n_neg; i++) neg_sum += exp(omni_cosine_sim(anchor, negs[i], d) / temp);
    return -log(pos_score / (pos_score + neg_sum + 1e-9));
}
