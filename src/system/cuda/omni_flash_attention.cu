// OMNI System Layer — CUDA Flash Attention Kernel
// Tiled fused attention with online softmax for GPU inference.

#include <cuda_runtime.h>
#include <cuda_fp16.h>
#include <float.h>

#define TILE_SIZE 64
#define WARP_SIZE 32

__device__ __forceinline__ float warp_reduce_max(float val) {
    for (int offset = WARP_SIZE / 2; offset > 0; offset >>= 1)
        val = fmaxf(val, __shfl_down_sync(0xffffffff, val, offset));
    return val;
}

__device__ __forceinline__ float warp_reduce_sum(float val) {
    for (int offset = WARP_SIZE / 2; offset > 0; offset >>= 1)
        val += __shfl_down_sync(0xffffffff, val, offset);
    return val;
}

__global__ void omni_flash_attention_kernel(
    const float* __restrict__ Q,
    const float* __restrict__ K,
    const float* __restrict__ V,
    float* __restrict__ O,
    const int N,    // sequence length
    const int d,    // head dimension
    const float scale
) {
    const int batch_head = blockIdx.x;
    const int tid = threadIdx.x;

    extern __shared__ float smem[];
    float* s_q = smem;
    float* s_k = smem + TILE_SIZE * d;
    float* s_v = s_k + TILE_SIZE * d;
    float* s_scores = s_v + TILE_SIZE * d;

    const float* q_base = Q + batch_head * N * d;
    const float* k_base = K + batch_head * N * d;
    const float* v_base = V + batch_head * N * d;
    float* o_base = O + batch_head * N * d;

    // Process query tiles
    for (int q_start = 0; q_start < N; q_start += TILE_SIZE) {
        int q_idx = q_start + tid;
        float row_max = -FLT_MAX;
        float row_sum = 0.0f;
        float acc[128]; // max head_dim
        for (int i = 0; i < d; i++) acc[i] = 0.0f;

        // Load Q tile into shared memory
        if (q_idx < N) {
            for (int i = 0; i < d; i++)
                s_q[tid * d + i] = q_base[q_idx * d + i];
        }
        __syncthreads();

        // Process K/V tiles
        for (int kv_start = 0; kv_start < N; kv_start += TILE_SIZE) {
            int kv_idx = kv_start + tid;

            // Load K,V tile
            if (kv_idx < N) {
                for (int i = 0; i < d; i++) {
                    s_k[tid * d + i] = k_base[kv_idx * d + i];
                    s_v[tid * d + i] = v_base[kv_idx * d + i];
                }
            }
            __syncthreads();

            // Compute attention scores
            if (q_idx < N) {
                for (int j = 0; j < TILE_SIZE && (kv_start + j) < N; j++) {
                    // Causal mask
                    if (kv_start + j > q_idx) continue;

                    float score = 0.0f;
                    for (int i = 0; i < d; i++)
                        score += s_q[tid * d + i] * s_k[j * d + i];
                    score *= scale;

                    // Online softmax update
                    float new_max = fmaxf(row_max, score);
                    float exp_diff = expf(row_max - new_max);
                    float exp_score = expf(score - new_max);

                    float new_sum = row_sum * exp_diff + exp_score;

                    for (int i = 0; i < d; i++)
                        acc[i] = acc[i] * exp_diff + exp_score * s_v[j * d + i];

                    row_max = new_max;
                    row_sum = new_sum;
                }
            }
            __syncthreads();
        }

        // Write output
        if (q_idx < N && row_sum > 0.0f) {
            float inv_sum = 1.0f / row_sum;
            for (int i = 0; i < d; i++)
                o_base[q_idx * d + i] = acc[i] * inv_sum;
        }
    }
}

// Host launcher
extern "C" void omni_flash_attention(
    const float* Q, const float* K, const float* V, float* O,
    int batch_heads, int seq_len, int head_dim, cudaStream_t stream
) {
    float scale = 1.0f / sqrtf((float)head_dim);
    size_t smem_size = (3 * TILE_SIZE * head_dim + TILE_SIZE * TILE_SIZE) * sizeof(float);

    omni_flash_attention_kernel<<<batch_heads, TILE_SIZE, smem_size, stream>>>(
        Q, K, V, O, seq_len, head_dim, scale
    );
}
