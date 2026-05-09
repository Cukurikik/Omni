#ifndef OMNI_MOE_ROUTING_KERNELS_CUH
#define OMNI_MOE_ROUTING_KERNELS_CUH

#include <cuda_runtime.h>
#include <cstdint>

namespace omni {
namespace cuda {
namespace moe {

struct RoutingConfig {
    int batch_size;
    int seq_len;
    int num_experts;
    int top_k;
    int hidden_dim;
};

// Computes softmax routing probabilities and selects top-k experts per token
void launch_topk_routing_kernel(
    const float* gating_logits,
    float* routing_weights,
    int* expert_indices,
    const RoutingConfig& config,
    cudaStream_t stream
);

// Generates token-to-expert memory displacements for UCCL All-To-All
void launch_expert_displacement_kernel(
    const int* expert_indices,
    size_t* expert_counts,
    size_t* expert_displacements,
    const RoutingConfig& config,
    cudaStream_t stream
);

} // namespace moe
} // namespace cuda
} // namespace omni

#endif // OMNI_MOE_ROUTING_KERNELS_CUH
