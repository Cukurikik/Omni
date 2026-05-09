#include "omni_moe_routing_kernels.cuh"
#include <cmath>
#include <algorithm>

namespace omni {
namespace cuda {
namespace moe {

__global__ void topk_routing_kernel(
    const float* __restrict__ gating_logits,
    float* __restrict__ routing_weights,
    int* __restrict__ expert_indices,
    int num_tokens,
    int num_experts,
    int top_k
) {
    int token_idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (token_idx >= num_tokens) return;

    const float* logits_row = gating_logits + (token_idx * num_experts);
    
    // Find max for numerical stability
    float max_val = -1e20f;
    for (int i = 0; i < num_experts; ++i) {
        max_val = fmaxf(max_val, logits_row[i]);
    }

    // Compute softmax denominator
    float sum_exp = 0.0f;
    for (int i = 0; i < num_experts; ++i) {
        sum_exp += expf(logits_row[i] - max_val);
    }

    // Since num_experts is typically small (e.g., 8, 16, 64), 
    // doing a naive local selection array is highly efficient in thread local memory.
    float local_probs[128]; // Max 128 experts supported in this kernel
    int num_e = min(num_experts, 128);
    for (int i = 0; i < num_e; ++i) {
        local_probs[i] = expf(logits_row[i] - max_val) / sum_exp;
    }

    // Simple Top-K selection (Bubble select for small K)
    float selected_weights[8]; // Max top-k = 8
    int selected_indices[8];
    int tk = min(top_k, 8);

    for (int k = 0; k < tk; ++k) {
        float max_prob = -1.0f;
        int max_idx = -1;
        for (int i = 0; i < num_e; ++i) {
            if (local_probs[i] > max_prob) {
                max_prob = local_probs[i];
                max_idx = i;
            }
        }
        selected_weights[k] = max_prob;
        selected_indices[k] = max_idx;
        local_probs[max_idx] = -1.0f; // mark as selected
    }

    // Normalize Top-K weights
    float topk_sum = 0.0f;
    for (int k = 0; k < tk; ++k) {
        topk_sum += selected_weights[k];
    }

    for (int k = 0; k < tk; ++k) {
        routing_weights[token_idx * top_k + k] = selected_weights[k] / topk_sum;
        expert_indices[token_idx * top_k + k] = selected_indices[k];
    }
}

void launch_topk_routing_kernel(
    const float* gating_logits,
    float* routing_weights,
    int* expert_indices,
    const RoutingConfig& config,
    cudaStream_t stream
) {
    int num_tokens = config.batch_size * config.seq_len;
    int threads = 256;
    int blocks = (num_tokens + threads - 1) / threads;
    
    topk_routing_kernel<<<blocks, threads, 0, stream>>>(
        gating_logits, routing_weights, expert_indices, num_tokens, config.num_experts, config.top_k
    );
}

} // namespace moe
} // namespace cuda
} // namespace omni
