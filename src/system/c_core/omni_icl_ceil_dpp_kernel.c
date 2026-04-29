/* Omni ICL-CEIL DPP Kernel (C) */
/* Ref: HKUNLP/icl-ceil — ICML 2023 */
#include <math.h>
void omni_dpp_kernel(const double* embeddings, int n, int d, double* kernel) {
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) {
            double dot = 0;
            for (int k = 0; k < d; k++) dot += embeddings[i*d+k] * embeddings[j*d+k];
            kernel[i*n+j] = dot;
        }
}
int omni_greedy_dpp(const double* kernel, int n, int k, int* selected) {
    int count = 0; int remaining[512];
    for (int i = 0; i < n && i < 512; i++) remaining[i] = i;
    int n_rem = n < 512 ? n : 512;
    for (int s = 0; s < k && s < n_rem; s++) {
        int best = -1; double best_score = -1e30;
        for (int r = 0; r < n_rem; r++) {
            int i = remaining[r]; double gain = kernel[i*n+i];
            for (int j = 0; j < count; j++)
                gain -= kernel[i*n+selected[j]] * kernel[i*n+selected[j]] / (kernel[selected[j]*n+selected[j]] + 1e-9);
            if (gain > best_score) { best_score = gain; best = r; }
        }
        if (best >= 0) { selected[count++] = remaining[best]; remaining[best] = remaining[--n_rem]; }
    }
    return count;
}
