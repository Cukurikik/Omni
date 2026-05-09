// OMNI System Layer — CUDA Attention Kernel Interface
// Flash-style tiled attention for GPU acceleration.
// Learned from: Dao-AILab/flash-attention, NVIDIA CUTLASS
// File: attention_kernel.cuh

#pragma once

#include <cuda_runtime.h>
#include <cuda_fp16.h>
#include <cmath>
#include <cstdint>

namespace omni {
namespace system {
namespace attention {

// Kernel configuration
struct AttentionKernelConfig {
    int batch_size;
    int num_heads;
    int seq_len_q;
    int seq_len_k;
    int head_dim;
    float scale;
    bool causal;
    int block_size_q;  // Tile size for Q dimension
    int block_size_k;  // Tile size for K dimension
};

// Tile-based attention score computation
template <int BLOCK_Q, int BLOCK_K, int HEAD_DIM>
__global__ void tiled_attention_forward_kernel(
    const float* __restrict__ Q,  // [B, H, S_q, D]
    const float* __restrict__ K,  // [B, H, S_k, D]
    const float* __restrict__ V,  // [B, H, S_k, D]
    float* __restrict__ O,        // [B, H, S_q, D]
    const int batch_size,
    const int num_heads,
    const int seq_len_q,
    const int seq_len_k,
    const float scale,
    const bool causal
) {
    const int b = blockIdx.z;
    const int h = blockIdx.y;
    const int q_tile_idx = blockIdx.x;
    const int tid = threadIdx.x;

    const int q_start = q_tile_idx * BLOCK_Q;
    const int q_end = min(q_start + BLOCK_Q, seq_len_q);

    if (q_start >= seq_len_q) return;

    // Base pointers for this batch and head
    const int bh_offset = (b * num_heads + h) * seq_len_q * HEAD_DIM;
    const int bh_offset_k = (b * num_heads + h) * seq_len_k * HEAD_DIM;

    // Shared memory for Q, K tiles
    __shared__ float s_Q[BLOCK_Q][HEAD_DIM];
    __shared__ float s_K[BLOCK_K][HEAD_DIM];
    __shared__ float s_V[BLOCK_K][HEAD_DIM];

    // Online softmax accumulators per query position
    float row_max[BLOCK_Q];
    float row_sum[BLOCK_Q];
    float output_acc[BLOCK_Q][HEAD_DIM];

    // Initialize accumulators
    for (int qi = 0; qi < BLOCK_Q && q_start + qi < seq_len_q; qi++) {
        row_max[qi] = -INFINITY;
        row_sum[qi] = 0.0f;
        for (int d = 0; d < HEAD_DIM; d++) {
            output_acc[qi][d] = 0.0f;
        }
    }

    // Load Q tile to shared memory
    for (int qi = 0; qi < BLOCK_Q && q_start + qi < seq_len_q; qi++) {
        for (int d = tid; d < HEAD_DIM; d += blockDim.x) {
            s_Q[qi][d] = Q[bh_offset + (q_start + qi) * HEAD_DIM + d];
        }
    }
    __syncthreads();

    // Iterate over K/V tiles
    const int num_k_tiles = (seq_len_k + BLOCK_K - 1) / BLOCK_K;
    for (int kt = 0; kt < num_k_tiles; kt++) {
        const int k_start = kt * BLOCK_K;
        const int k_end = min(k_start + BLOCK_K, seq_len_k);

        // Load K and V tiles
        for (int ki = 0; ki < BLOCK_K && k_start + ki < seq_len_k; ki++) {
            for (int d = tid; d < HEAD_DIM; d += blockDim.x) {
                s_K[ki][d] = K[bh_offset_k + (k_start + ki) * HEAD_DIM + d];
                s_V[ki][d] = V[bh_offset_k + (k_start + ki) * HEAD_DIM + d];
            }
        }
        __syncthreads();

        // Compute attention scores for this tile
        for (int qi = 0; qi < BLOCK_Q && q_start + qi < seq_len_q; qi++) {
            for (int ki = 0; ki < BLOCK_K && k_start + ki < seq_len_k; ki++) {
                // Causal masking
                if (causal && (k_start + ki) > (q_start + qi)) continue;

                // Dot product Q[qi] · K[ki]
                float score = 0.0f;
                for (int d = 0; d < HEAD_DIM; d++) {
                    score += s_Q[qi][d] * s_K[ki][d];
                }
                score *= scale;

                // Online softmax update
                float prev_max = row_max[qi];
                row_max[qi] = fmaxf(row_max[qi], score);
                float exp_prev = expf(prev_max - row_max[qi]);
                float exp_score = expf(score - row_max[qi]);

                // Rescale previous accumulation
                row_sum[qi] = row_sum[qi] * exp_prev + exp_score;
                for (int d = 0; d < HEAD_DIM; d++) {
                    output_acc[qi][d] = output_acc[qi][d] * exp_prev + exp_score * s_V[ki][d];
                }
            }
        }
        __syncthreads();
    }

    // Write output (normalize by softmax denominator)
    for (int qi = 0; qi < BLOCK_Q && q_start + qi < seq_len_q; qi++) {
        float inv_sum = 1.0f / fmaxf(row_sum[qi], 1e-6f);
        for (int d = tid; d < HEAD_DIM; d += blockDim.x) {
            O[bh_offset + (q_start + qi) * HEAD_DIM + d] = output_acc[qi][d] * inv_sum;
        }
    }
}

// Launch configuration helper
inline void launch_tiled_attention(
    const float* Q, const float* K, const float* V, float* O,
    const AttentionKernelConfig& cfg, cudaStream_t stream = 0
) {
    constexpr int BLOCK_Q = 32;
    constexpr int BLOCK_K = 32;
    constexpr int HEAD_DIM = 64;

    dim3 grid(
        (cfg.seq_len_q + BLOCK_Q - 1) / BLOCK_Q,
        cfg.num_heads,
        cfg.batch_size
    );
    dim3 block(HEAD_DIM);

    tiled_attention_forward_kernel<BLOCK_Q, BLOCK_K, HEAD_DIM><<<grid, block, 0, stream>>>(
        Q, K, V, O,
        cfg.batch_size, cfg.num_heads,
        cfg.seq_len_q, cfg.seq_len_k,
        cfg.scale, cfg.causal
    );
}

}  // namespace attention
}  // namespace system
}  // namespace omni
