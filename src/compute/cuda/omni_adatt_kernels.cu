#include "omni_adatt_kernels.cuh"

// OMNI MOTHER: AdaTT Fusion Kernel
// Fast cross-task fusion for recommendation systems

__global__ void omni_adatt_fusion_kernel(
    const float* task_embeddings,
    float* fused_embeddings,
    const float* fusion_weights,
    int num_tasks,
    int hidden_dim
) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid < hidden_dim) {
        for (int t = 0; t < num_tasks; t++) {
            float val = 0.0f;
            for (int other_t = 0; other_t < num_tasks; other_t++) {
                val += fusion_weights[t * num_tasks + other_t] * task_embeddings[other_t * hidden_dim + tid];
            }
            fused_embeddings[t * hidden_dim + tid] = val;
        }
    }
}

extern "C" {
void omni_adatt_fuse(const float* in, float* out, const float* weights, int tasks, int dim, cudaStream_t stream) {
    int blocks = (dim + 255) / 256;
    omni_adatt_fusion_kernel<<<blocks, 256, 0, stream>>>(in, out, weights, tasks, dim);
}
}
