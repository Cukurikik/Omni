// Omni BabyGPT Attention Kernel (C++)
// Ref: TatevKaren/BabyGPT-Build_GPT_From_Scratch
#include <cmath>
#include <cstddef>
void omni_softmax(float* x, int n) {
    float mx = x[0];
    for (int i = 1; i < n; i++) if (x[i] > mx) mx = x[i];
    float sum = 0;
    for (int i = 0; i < n; i++) { x[i] = expf(x[i] - mx); sum += x[i]; }
    for (int i = 0; i < n; i++) x[i] /= sum;
}
void omni_attention_scores(const float* Q, const float* K, float* out,
                            int seq_len, int d_k) {
    float scale = sqrtf((float)d_k);
    for (int i = 0; i < seq_len; i++)
        for (int j = 0; j < seq_len; j++) {
            float dot = 0;
            for (int d = 0; d < d_k; d++) dot += Q[i*d_k+d] * K[j*d_k+d];
            out[i*seq_len+j] = dot / scale;
        }
    for (int i = 0; i < seq_len; i++) omni_softmax(out + i*seq_len, seq_len);
}
