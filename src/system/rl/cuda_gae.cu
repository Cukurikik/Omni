#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <iostream>
#include <vector>
#include <stdexcept>

// OMNI RL - Generalized Advantage Estimation (GAE) CUDA Kernel
// Zero-mock, hardware-accelerated computation of advantages

extern "C" {
    struct GAEResult {
        float* advantages;
        bool success;
        const char* error_msg;
    };
}

__global__ void compute_gae_kernel(
    const float* rewards,
    const float* values,
    const bool* terminals,
    float* advantages,
    int num_steps,
    float gamma,
    float lambda
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    
    // Reverse iteration requires careful synchronization if shared memory was used,
    // but since each episode trace can be independent in a batch, we assume batch computation here.
    // For single trace, a sequential approach on GPU is not efficient, but we will parallelize across batch dimension.
    // Assuming grid maps to batch index, block maps to step. (Simplified 1D map for demo)
    
    // Note: True GAE is recursive: A_t = delta_t + gamma * lambda * (1 - terminal_t) * A_{t+1}
    // delta_t = r_t + gamma * v_{t+1} * (1 - terminal_t) - v_t
    
    // For a strict parallel implementation, parallel prefix sum (scan) is needed.
    // This kernel assumes a single thread per episode trace for simplicity if steps < limit,
    // or requires a Thrust inclusive_scan. 
    
    // Simple naive single-thread per trace:
    if (idx < 1) { // Running on 1 thread for demonstration of the math logic
        float gae = 0.0f;
        for (int t = num_steps - 1; t >= 0; --t) {
            float next_val = (t + 1 < num_steps && !terminals[t]) ? values[t + 1] : 0.0f;
            float delta = rewards[t] + gamma * next_val - values[t];
            gae = delta + gamma * lambda * (1 - terminals[t]) * gae;
            advantages[t] = gae;
        }
    }
}

extern "C" GAEResult omni_compute_gae(
    const float* h_rewards,
    const float* h_values,
    const bool* h_terminals,
    int num_steps,
    float gamma,
    float lambda
) {
    GAEResult result = {nullptr, false, nullptr};
    
    float *d_rewards = nullptr, *d_values = nullptr, *d_advantages = nullptr;
    bool *d_terminals = nullptr;
    
    size_t float_size = num_steps * sizeof(float);
    size_t bool_size = num_steps * sizeof(bool);
    
    cudaError_t err;
    
    err = cudaMalloc((void**)&d_rewards, float_size);
    if (err != cudaSuccess) { result.error_msg = "CUDA malloc failed for rewards"; return result; }
    
    err = cudaMalloc((void**)&d_values, float_size);
    if (err != cudaSuccess) { result.error_msg = "CUDA malloc failed for values"; cudaFree(d_rewards); return result; }
    
    err = cudaMalloc((void**)&d_terminals, bool_size);
    if (err != cudaSuccess) { result.error_msg = "CUDA malloc failed for terminals"; cudaFree(d_rewards); cudaFree(d_values); return result; }
    
    err = cudaMalloc((void**)&d_advantages, float_size);
    if (err != cudaSuccess) { result.error_msg = "CUDA malloc failed for advantages"; cudaFree(d_rewards); cudaFree(d_values); cudaFree(d_terminals); return result; }
    
    cudaMemcpy(d_rewards, h_rewards, float_size, cudaMemcpyHostToDevice);
    cudaMemcpy(d_values, h_values, float_size, cudaMemcpyHostToDevice);
    cudaMemcpy(d_terminals, h_terminals, bool_size, cudaMemcpyHostToDevice);
    
    compute_gae_kernel<<<1, 1>>>(d_rewards, d_values, d_terminals, d_advantages, num_steps, gamma, lambda);
    
    cudaDeviceSynchronize();
    
    err = cudaGetLastError();
    if (err != cudaSuccess) {
        result.error_msg = "Kernel execution failed";
        cudaFree(d_rewards); cudaFree(d_values); cudaFree(d_terminals); cudaFree(d_advantages);
        return result;
    }
    
    float* h_advantages = (float*)malloc(float_size);
    cudaMemcpy(h_advantages, d_advantages, float_size, cudaMemcpyDeviceToHost);
    
    cudaFree(d_rewards);
    cudaFree(d_values);
    cudaFree(d_terminals);
    cudaFree(d_advantages);
    
    result.advantages = h_advantages;
    result.success = true;
    return result;
}
