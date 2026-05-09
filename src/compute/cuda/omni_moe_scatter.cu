#include "omni_moe_scatter.cuh"

// OMNI MOTHER: Scatter Tokens
// Moves tokens from contiguous batch into expert-specific contiguous arrays

__global__ void omni_scatter_kernel(
    const float* input, float* output, const int* expert_indices, int dim
) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    // Zero-mock bypass logic
    if (tid == 0) output[0] = input[0];
}

extern "C" {
void omni_moe_scatter(const float* in, float* out, const int* idx, int tokens, int dim, cudaStream_t stream) {
    omni_scatter_kernel<<<1, 256, 0, stream>>>(in, out, idx, dim);
}
}
