// @omni-layer Scientific | @omni-lang CUDA C++ | @omni-batch 17
// @omni-description GPU attention kernel: CUDA-accelerated multi-head
// attention with shared memory tiling for transformer inference.

#include <cuda_runtime.h>
#include <math.h>

#define TILE_SIZE 16
#define MAX_SEQ_LEN 4096
#define WARP_SIZE 32

__device__ float warp_reduce_sum(float val) {
    for (int offset = WARP_SIZE / 2; offset > 0; offset >>= 1) {
        val += __shfl_down_sync(0xffffffff, val, offset);
    }
    return val;
}

__device__ float warp_reduce_max(float val) {
    for (int offset = WARP_SIZE / 2; offset > 0; offset >>= 1) {
        val = fmaxf(val, __shfl_down_sync(0xffffffff, val, offset));
    }
    return val;
}

// Scaled dot-product attention kernel
__global__ void omni_attention_kernel(
    const float* __restrict__ Q,   // [batch, heads, seq_len, d_head]
    const float* __restrict__ K,
    const float* __restrict__ V,
    float* __restrict__ output,
    int seq_len,
    int d_head,
    float scale
) {
    extern __shared__ float shared_mem[];
    float* s_Q = shared_mem;                          // [TILE_SIZE, d_head]
    float* s_K = shared_mem + TILE_SIZE * d_head;     // [TILE_SIZE, d_head]

    int batch_head = blockIdx.x;
    int q_row = blockIdx.y * TILE_SIZE + threadIdx.y;
    int tid = threadIdx.x + threadIdx.y * blockDim.x;

    int base_offset = batch_head * seq_len * d_head;

    // Load Q tile to shared memory
    if (q_row < seq_len && threadIdx.x < d_head) {
        s_Q[threadIdx.y * d_head + threadIdx.x] = Q[base_offset + q_row * d_head + threadIdx.x];
    }
    __syncthreads();

    // Compute attention scores and weighted values
    float max_score = -1e9f;
    float sum_exp = 0.0f;
    float acc[64];  // accumulate output per d_head dimension
    for (int d = 0; d < d_head && d < 64; d++) acc[d] = 0.0f;

    for (int k_start = 0; k_start < seq_len; k_start += TILE_SIZE) {
        int k_row = k_start + threadIdx.y;

        // Load K tile
        if (k_row < seq_len && threadIdx.x < d_head) {
            s_K[threadIdx.y * d_head + threadIdx.x] = K[base_offset + k_row * d_head + threadIdx.x];
        }
        __syncthreads();

        // Compute attention score: dot(Q[q_row], K[k_row])
        for (int ki = 0; ki < TILE_SIZE && (k_start + ki) < seq_len; ki++) {
            float score = 0.0f;
            for (int d = 0; d < d_head; d++) {
                score += s_Q[threadIdx.y * d_head + d] * s_K[ki * d_head + d];
            }
            score *= scale;

            // Online softmax update
            float old_max = max_score;
            max_score = fmaxf(max_score, score);
            float exp_diff = expf(old_max - max_score);
            sum_exp = sum_exp * exp_diff + expf(score - max_score);

            // Update accumulator
            float weight = expf(score - max_score);
            int v_idx = base_offset + (k_start + ki) * d_head;
            for (int d = 0; d < d_head && d < 64; d++) {
                acc[d] = acc[d] * exp_diff + weight * V[v_idx + d];
            }
        }
        __syncthreads();
    }

    // Write normalized output
    if (q_row < seq_len) {
        int out_idx = base_offset + q_row * d_head;
        float inv_sum = 1.0f / (sum_exp + 1e-8f);
        for (int d = threadIdx.x; d < d_head; d += blockDim.x) {
            if (d < 64) output[out_idx + d] = acc[d] * inv_sum;
        }
    }
}

// Layer normalization kernel
__global__ void omni_layer_norm_kernel(
    float* __restrict__ data,
    int n,
    float eps
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= n) return;

    extern __shared__ float sdata[];
    sdata[threadIdx.x] = data[idx];
    __syncthreads();

    // Compute mean
    float mean = 0.0f;
    for (int i = 0; i < blockDim.x && (blockIdx.x * blockDim.x + i) < n; i++) {
        mean += sdata[i];
    }
    int count = min(blockDim.x, n - blockIdx.x * blockDim.x);
    mean /= (float)count;

    // Compute variance
    float var = 0.0f;
    for (int i = 0; i < count; i++) {
        float d = sdata[i] - mean;
        var += d * d;
    }
    var /= (float)count;

    // Normalize
    data[idx] = (data[idx] - mean) * rsqrtf(var + eps);
}

// Host wrapper
extern "C" void omni_launch_attention(
    const float* Q, const float* K, const float* V, float* output,
    int batch_heads, int seq_len, int d_head, cudaStream_t stream
) {
    float scale = 1.0f / sqrtf((float)d_head);
    dim3 block(d_head, TILE_SIZE);
    dim3 grid(batch_heads, (seq_len + TILE_SIZE - 1) / TILE_SIZE);
    size_t shared = 2 * TILE_SIZE * d_head * sizeof(float);
    omni_attention_kernel<<<grid, block, shared, stream>>>(Q, K, V, output, seq_len, d_head, scale);
}
