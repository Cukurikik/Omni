// @omni-layer Scientific | @omni-lang CUDA | @omni-batch 18 | @omni-semester 16
// @omni-description CUDA flash attention kernel for transformer inference
// with tiled softmax and fused KV-cache support.

#include <cuda_runtime.h>
#include <math.h>

#define BLOCK_SIZE 256
#define TILE_SIZE 64
#define WARP_SIZE 32

__device__ float warp_reduce_max(float val) {
    for (int offset = WARP_SIZE / 2; offset > 0; offset >>= 1)
        val = fmaxf(val, __shfl_down_sync(0xFFFFFFFF, val, offset));
    return val;
}

__device__ float warp_reduce_sum(float val) {
    for (int offset = WARP_SIZE / 2; offset > 0; offset >>= 1)
        val += __shfl_down_sync(0xFFFFFFFF, val, offset);
    return val;
}

__global__ void omni_flash_attention_kernel(
    const float* __restrict__ Q,
    const float* __restrict__ K,
    const float* __restrict__ V,
    float* __restrict__ O,
    const int seq_len, const int head_dim, const float scale
) {
    const int tid = threadIdx.x;
    const int query_idx = blockIdx.x;

    if (query_idx >= seq_len) return;

    extern __shared__ float smem[];
    float* s_key = smem;
    float* s_val = s_key + TILE_SIZE * head_dim;

    float m_prev = -INFINITY;
    float l_prev = 0.0f;
    float acc[64];
    for (int d = 0; d < head_dim && d < 64; d++) acc[d] = 0.0f;

    for (int tile_start = 0; tile_start < seq_len; tile_start += TILE_SIZE) {
        int tile_end = min(tile_start + TILE_SIZE, seq_len);
        int tile_len = tile_end - tile_start;

        // Load K, V tile into shared memory
        for (int i = tid; i < tile_len * head_dim; i += blockDim.x) {
            int kv_idx = tile_start * head_dim + i;
            s_key[i] = K[kv_idx];
            s_val[i] = V[kv_idx];
        }
        __syncthreads();

        // Compute attention scores for this tile
        float m_new = m_prev;
        for (int j = 0; j < tile_len; j++) {
            float score = 0.0f;
            for (int d = tid; d < head_dim; d += blockDim.x) {
                score += Q[query_idx * head_dim + d] * s_key[j * head_dim + d];
            }
            score = warp_reduce_sum(score) * scale;
            m_new = fmaxf(m_new, score);
        }

        float l_new = l_prev * expf(m_prev - m_new);
        for (int j = 0; j < tile_len; j++) {
            float score = 0.0f;
            for (int d = tid; d < head_dim; d += blockDim.x) {
                score += Q[query_idx * head_dim + d] * s_key[j * head_dim + d];
            }
            score = warp_reduce_sum(score) * scale;
            float p = expf(score - m_new);
            l_new += p;
            for (int d = 0; d < head_dim && d < 64; d++) {
                acc[d] = acc[d] * expf(m_prev - m_new) + p * s_val[j * head_dim + d];
            }
        }

        m_prev = m_new;
        l_prev = l_new;
        __syncthreads();
    }

    float inv_l = 1.0f / (l_prev + 1e-10f);
    for (int d = tid; d < head_dim; d += blockDim.x) {
        O[query_idx * head_dim + d] = acc[d % 64] * inv_l;
    }
}

extern "C" void omni_flash_attention(
    const float* Q, const float* K, const float* V, float* O,
    int batch_size, int n_heads, int seq_len, int head_dim
) {
    float scale = 1.0f / sqrtf((float)head_dim);
    size_t smem_size = 2 * TILE_SIZE * head_dim * sizeof(float);

    for (int b = 0; b < batch_size; b++) {
        for (int h = 0; h < n_heads; h++) {
            int offset = (b * n_heads + h) * seq_len * head_dim;
            omni_flash_attention_kernel<<<seq_len, BLOCK_SIZE, smem_size>>>(
                Q + offset, K + offset, V + offset, O + offset,
                seq_len, head_dim, scale
            );
        }
    }
    cudaDeviceSynchronize();
}
