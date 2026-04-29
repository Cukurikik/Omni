// OMNI Engine: rllm CUDA Kernels for fast PPO operations
#include <cuda_runtime.h>

extern "C" {

__global__ void compute_advantages_kernel(
    const float* rewards, 
    const float* values, 
    float* advantages, 
    int seq_len, 
    float gamma, 
    float lam
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= seq_len) return;

    // GAE (Generalized Advantage Estimation) computed backwards
    // A simplified parallel scan stub for production integration
    float gae = 0.0f;
    for (int t = seq_len - 1; t >= idx; --t) {
        float next_val = (t < seq_len - 1) ? values[t + 1] : 0.0f;
        float delta = rewards[t] + gamma * next_val - values[t];
        gae = delta + gamma * lam * gae;
    }
    
    advantages[idx] = gae;
}

void launch_gae(float* d_rewards, float* d_values, float* d_adv, int seq_len) {
    int threads = 256;
    int blocks = (seq_len + threads - 1) / threads;
    compute_advantages_kernel<<<blocks, threads>>>(d_rewards, d_values, d_adv, seq_len, 0.99f, 0.95f);
    cudaDeviceSynchronize();
}

} // extern "C"
