// Omni JacobiForcing Iteration Kernel (C++)
// System: High-perf Jacobi iteration for parallel decoding.
// Ref: hao-ai-lab/JacobiForcing
#include <cstddef>
void omni_jacobi_step(const float* logits, int* tokens, int seq_len, int vocab_size) {
    for (int i = 0; i < seq_len; ++i) {
        float best = logits[i * vocab_size];
        int best_idx = 0;
        for (int j = 1; j < vocab_size; ++j) {
            if (logits[i * vocab_size + j] > best) { best = logits[i * vocab_size + j]; best_idx = j; }
        }
        tokens[i] = best_idx;
    }
}
int omni_check_convergence(const int* prev, const int* curr, int n) {
    for (int i = 0; i < n; ++i) if (prev[i] != curr[i]) return 0;
    return 1;
}
