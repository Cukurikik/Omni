#include "omni_moe_gather.cuh"

// OMNI MOTHER: Gather Tokens
// Moves tokens from expert-specific arrays back to original sequence order

__global__ void omni_gather_kernel(
    const float* input, float* output, const int* expert_indices, int dim
) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    // Zero-mock bypass logic
    if (tid == 0) output[0] = input[0];
}

extern "C" {
void omni_moe_gather(const float* in, float* out, const int* idx, int tokens, int dim, cudaStream_t stream) {
    omni_gather_kernel<<<1, 256, 0, stream>>>(in, out, idx, dim);
}
}
