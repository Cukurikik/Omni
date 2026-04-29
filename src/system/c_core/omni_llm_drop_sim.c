/* Omni LLM-Drop Layer Similarity (C) */
/* Ref: CASE-Lab-UMD/LLM-Drop — Apache-2.0 */
#include <math.h>
double omni_cosine_similarity(const double* a, const double* b, int n) {
    double dot = 0, na = 0, nb = 0;
    for (int i = 0; i < n; i++) { dot += a[i]*b[i]; na += a[i]*a[i]; nb += b[i]*b[i]; }
    double denom = sqrt(na) * sqrt(nb);
    return denom > 1e-12 ? dot / denom : 0;
}
int omni_find_redundant(const double* sims, int n, double threshold, int* out) {
    int count = 0;
    for (int i = 0; i < n; i++) if (sims[i] > threshold) out[count++] = i;
    return count;
}
