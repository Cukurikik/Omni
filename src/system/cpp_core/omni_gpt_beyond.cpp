#include <vector>
#include <cmath>

namespace OmniGPT {
    void compute_attention(const float* q, const float* k, const float* v, float* out, int seq_len, int dim) {
        for (int i = 0; i < seq_len; ++i) {
            float sum_exp = 0.0f;
            std::vector<float> scores(seq_len, 0.0f);
            for (int j = 0; j < seq_len; ++j) {
                float score = 0.0f;
                for (int d = 0; d < dim; ++d) {
                    score += q[i * dim + d] * k[j * dim + d];
                }
                score /= std::sqrt(static_cast<float>(dim));
                scores[j] = std::exp(score);
                sum_exp += scores[j];
            }
            for (int j = 0; j < seq_len; ++j) {
                for (int d = 0; d < dim; ++d) {
                    out[i * dim + d] += (scores[j] / sum_exp) * v[j * dim + d];
                }
            }
        }
    }
}
