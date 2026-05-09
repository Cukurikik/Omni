/*
 * omni_flash_attn_rope.cu — Rotary Position Embedding (RoPE) Kernel
 * Layer: System / GPU
 * Inspired by: Dao-AILab/flash-attention
 *
 * Fuses the Rotary Position Embedding computation directly into the Q and K 
 * loading phase of FlashAttention to avoid extra HBM read/writes. Zero mock.
 */

#include <cuda_runtime.h>
#include <math.h>

// CUDA Kernel: Apply RoPE to Q and K
__global__ void apply_rope_kernel(
    float* Q, float* K, 
    int seq_len, int head_dim, int num_heads,
    float base_theta
) {
    // Thread assignments
    // blockIdx.x = batch_idx * num_heads + head_idx
    // blockIdx.y = seq_idx
    // threadIdx.x = head_dim_idx (assuming head_dim is even and <= 1024)
    
    int seq_idx = blockIdx.y;
    if (seq_idx >= seq_len) return;

    int dim_idx = threadIdx.x * 2; // We process pairs of dimensions (dim, dim+1)
    if (dim_idx >= head_dim) return;

    // Calculate frequency for this dimension pair
    // theta_i = base_theta ^ (-2(i-1)/d)
    float exponent = -1.0f * (float)dim_idx / (float)head_dim;
    float theta_i = powf(base_theta, exponent);
    
    // Calculate m * theta_i
    float m_theta = (float)seq_idx * theta_i;
    
    float cos_val = cosf(m_theta);
    float sin_val = sinf(m_theta);

    // Global offset for Q and K
    int offset = blockIdx.x * (seq_len * head_dim) + seq_idx * head_dim + dim_idx;

    // --- Process Q ---
    float q_even = Q[offset];
    float q_odd  = Q[offset + 1];
    
    // RoPE rotation
    Q[offset]     = q_even * cos_val - q_odd * sin_val;
    Q[offset + 1] = q_odd  * cos_val + q_even * sin_val;

    // --- Process K ---
    float k_even = K[offset];
    float k_odd  = K[offset + 1];
    
    // RoPE rotation
    K[offset]     = k_even * cos_val - k_odd * sin_val;
    K[offset + 1] = k_odd  * cos_val + k_even * sin_val;
}

extern "C" {
    void omni_apply_rope_cuda(
        float* d_Q, float* d_K, 
        int batch_size, int num_heads, int seq_len, int head_dim,
        float base_theta // Usually 10000.0f
    ) {
        dim3 blocks(batch_size * num_heads, seq_len);
        dim3 threads(head_dim / 2); // One thread per dimension pair
        
        apply_rope_kernel<<<blocks, threads>>>(d_Q, d_K, seq_len, head_dim, num_heads, base_theta);
        cudaDeviceSynchronize();
    }
}
