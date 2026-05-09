// @omni-layer System | @omni-lang C++ | @omni-batch 18 | @omni-semester 16
// @omni-repo Rishit-dagli/Fast-Transformer + wgcban/HyperTransformer
// @omni-description Fast attention + Hyper fusion: C++ optimized additive
// attention with O(n) complexity and spectral feature fusion kernel.

#pragma once
#include <cmath>
#include <vector>
#include <algorithm>
#include <numeric>

namespace omni::transformer {

struct FastAttentionConfig {
    int d_model = 768;
    int n_heads = 12;
    int seq_len = 512;
    float dropout = 0.0f;
};

// Additive attention O(n) — Fast Transformer pattern
class FastAdditiveAttention {
    int d_model_, n_heads_, head_dim_;
    float scale_;
public:
    explicit FastAdditiveAttention(int d_model, int n_heads)
        : d_model_(d_model), n_heads_(n_heads),
          head_dim_(d_model / n_heads),
          scale_(1.0f / std::sqrt(static_cast<float>(d_model / n_heads))) {}

    // Global context vector approach: O(n*d) instead of O(n^2)
    std::vector<float> forward(const std::vector<float>& Q,
                                const std::vector<float>& K,
                                const std::vector<float>& V,
                                int seq_len) const {
        std::vector<float> output(seq_len * d_model_, 0.0f);

        for (int h = 0; h < n_heads_; h++) {
            int off = h * head_dim_;

            // Compute global context: weighted sum of V using softmax(W_q * Q_global)
            std::vector<float> global_query(head_dim_, 0.0f);
            for (int i = 0; i < seq_len; i++) {
                for (int d = 0; d < head_dim_; d++) {
                    global_query[d] += Q[i * d_model_ + off + d];
                }
            }
            for (int d = 0; d < head_dim_; d++) {
                global_query[d] /= static_cast<float>(seq_len);
            }

            // Attention weights: alpha_i = softmax(K_i . global_query)
            std::vector<float> alpha(seq_len);
            float max_score = -1e9f;
            for (int i = 0; i < seq_len; i++) {
                float dot = 0.0f;
                for (int d = 0; d < head_dim_; d++) {
                    dot += K[i * d_model_ + off + d] * global_query[d];
                }
                alpha[i] = dot * scale_;
                max_score = std::max(max_score, alpha[i]);
            }
            float sum_exp = 0.0f;
            for (int i = 0; i < seq_len; i++) {
                alpha[i] = std::exp(alpha[i] - max_score);
                sum_exp += alpha[i];
            }
            for (int i = 0; i < seq_len; i++) {
                alpha[i] /= (sum_exp + 1e-10f);
            }

            // Global context value
            std::vector<float> ctx(head_dim_, 0.0f);
            for (int i = 0; i < seq_len; i++) {
                for (int d = 0; d < head_dim_; d++) {
                    ctx[d] += alpha[i] * V[i * d_model_ + off + d];
                }
            }

            // Broadcast global context + local residual
            for (int i = 0; i < seq_len; i++) {
                for (int d = 0; d < head_dim_; d++) {
                    output[i * d_model_ + off + d] = ctx[d] + V[i * d_model_ + off + d] * 0.5f;
                }
            }
        }
        return output;
    }
};

// HyperTransformer spectral feature fusion
class SpectralFusion {
    int low_dim_, high_dim_, fused_dim_;
public:
    SpectralFusion(int low_dim, int high_dim, int fused_dim)
        : low_dim_(low_dim), high_dim_(high_dim), fused_dim_(fused_dim) {}

    std::vector<float> fuse(const std::vector<float>& low_res,
                             const std::vector<float>& high_res) const {
        std::vector<float> fused(fused_dim_, 0.0f);
        for (int d = 0; d < fused_dim_; d++) {
            float lo = (d < static_cast<int>(low_res.size())) ? low_res[d] : 0.0f;
            float hi = (d < static_cast<int>(high_res.size())) ? high_res[d] : 0.0f;
            float gate = 1.0f / (1.0f + std::exp(-(lo * hi * 10.0f)));
            fused[d] = gate * hi + (1.0f - gate) * lo;
        }
        return fused;
    }
};

// Layer norm
inline void layer_norm(std::vector<float>& x, float eps = 1e-5f) {
    float mean = std::accumulate(x.begin(), x.end(), 0.0f) / x.size();
    float var = 0.0f;
    for (float v : x) { float d = v - mean; var += d * d; }
    var /= x.size();
    float inv = 1.0f / std::sqrt(var + eps);
    for (float& v : x) v = (v - mean) * inv;
}

} // namespace omni::transformer
