#include <cmath>

extern "C" {
    void omni_sys_modes_compute_gate(const float* input, float* expert_weights, int dim, int num_experts) {
        if (!input || !expert_weights || dim <= 0 || num_experts <= 0) return;
        
        // Mock gating network with softmax
        float max_val = -1e9;
        for(int i=0; i<num_experts; ++i) {
            expert_weights[i] = input[i % dim] * 0.1f; // dummy projection
            if(expert_weights[i] > max_val) max_val = expert_weights[i];
        }
        
        float sum_exp = 0.0f;
        for(int i=0; i<num_experts; ++i) {
            expert_weights[i] = std::exp(expert_weights[i] - max_val);
            sum_exp += expert_weights[i];
        }
        
        for(int i=0; i<num_experts; ++i) {
            expert_weights[i] /= sum_exp;
        }
    }
}
