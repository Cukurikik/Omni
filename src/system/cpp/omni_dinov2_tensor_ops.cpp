// OMNI Framework - C++ Tensor Operations for DINOv2
// Fast local feature aggregation and attention map extraction

#include <vector>
#include <cmath>
#include <stdexcept>

class OmniDinoV2TensorOps {
public:
    static std::vector<float> compute_attention_weights(const std::vector<float>& queries, const std::vector<float>& keys, int d_k) {
        if (queries.size() != keys.size()) {
            throw std::invalid_argument("OMNI: Query and Key dimensions must match.");
        }

        std::vector<float> attention_scores(queries.size());
        float scale = std::sqrt(static_cast<float>(d_k));
        
        // Compute scaled dot-product attention
        for (size_t i = 0; i < queries.size(); ++i) {
            attention_scores[i] = (queries[i] * keys[i]) / scale;
        }

        // Softmax implementation
        float max_score = attention_scores[0];
        for (float score : attention_scores) {
            if (score > max_score) max_score = score;
        }

        float sum_exp = 0.0f;
        for (size_t i = 0; i < attention_scores.size(); ++i) {
            attention_scores[i] = std::exp(attention_scores[i] - max_score);
            sum_exp += attention_scores[i];
        }

        for (size_t i = 0; i < attention_scores.size(); ++i) {
            attention_scores[i] /= sum_exp;
        }

        return attention_scores;
    }
};
