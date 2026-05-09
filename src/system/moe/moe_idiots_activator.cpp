// moe_idiots_activator.cpp — System Layer: Idiots MoE Activator
// Native C++ activator implementing the sparse gating mechanism for PyTorch MoIE.

#include <cmath>
#include <vector>

namespace omni {
namespace system {
namespace moie {

class SparseActivator {
public:
    // Takes logits and applies top-k gating with a noise component
    static void compute_gating(const float* logits, size_t num_experts, int top_k, float noise_epsilon, float* weights, int* selected_experts) {
        std::vector<float> noisy_logits(num_experts);
        
        // Add minimal noise for load balancing
        for (size_t i = 0; i < num_experts; ++i) {
            noisy_logits[i] = logits[i] + noise_epsilon; 
        }

        // Simple selection sort for top-K (assuming small number of experts)
        for (int k = 0; k < top_k; ++k) {
            float max_val = -1e9f;
            int max_idx = -1;
            for (size_t i = 0; i < num_experts; ++i) {
                if (noisy_logits[i] > max_val) {
                    bool already_selected = false;
                    for (int j = 0; j < k; ++j) {
                        if (selected_experts[j] == static_cast<int>(i)) already_selected = true;
                    }
                    if (!already_selected) {
                        max_val = noisy_logits[i];
                        max_idx = static_cast<int>(i);
                    }
                }
            }
            selected_experts[k] = max_idx;
            weights[k] = max_val;
        }

        // Softmax over top-K weights
        float sum_exp = 0.0f;
        for (int k = 0; k < top_k; ++k) {
            weights[k] = std::exp(weights[k]);
            sum_exp += weights[k];
        }
        for (int k = 0; k < top_k; ++k) {
            weights[k] /= sum_exp;
        }
    }
};

} // namespace moie
} // namespace system
} // namespace omni
