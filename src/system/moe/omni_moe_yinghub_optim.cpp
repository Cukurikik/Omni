#include <iostream>
#include <vector>
#include <cmath>

// OMNI MOTHER Production Zero-Mock YingHub Training Optimizer
// C++ implementation of specific gradients clipping and scaling optimizations
// for high-quality autoregressive text generation (Shakespearean).

namespace omni {
namespace system {

class YingHubOptimizer {
private:
    float learning_rate;
    float max_grad_norm;

public:
    YingHubOptimizer(float lr = 1e-4, float clip_norm = 1.0f) 
        : learning_rate(lr), max_grad_norm(clip_norm) {}

    // In-place gradient clipping and weight update
    void step(std::vector<float>& weights, std::vector<float>& gradients) {
        if (weights.size() != gradients.size()) {
            throw std::invalid_argument("OMNI CRITICAL: Weight and gradient sizes mismatch.");
        }

        // 1. Calculate Global Norm
        float global_norm_sq = 0.0f;
        for (float g : gradients) {
            global_norm_sq += g * g;
        }
        float global_norm = std::sqrt(global_norm_sq);

        // 2. Scaling factor for clipping
        float clip_coef = max_grad_norm / (global_norm + 1e-6f);
        if (clip_coef > 1.0f) {
            clip_coef = 1.0f; // No clipping needed
        }

        // 3. Update Weights (Simple SGD logic for demonstration, AdamW is standard)
        for (size_t i = 0; i < weights.size(); ++i) {
            float clipped_grad = gradients[i] * clip_coef;
            weights[i] -= learning_rate * clipped_grad;
        }
    }
};

} // namespace system
} // namespace omni
