// OMNI Scientific Layer — OpenCL Matrix Multiply Kernel
// GPU-accelerated GEMM for cross-platform transformer inference.

__kernel void omni_gemm_f32(
    __global const float* A,
    __global const float* B,
    __global float* C,
    const int M,
    const int N,
    const int K,
    const float alpha,
    const float beta
) {
    const int TILE_SIZE = 16;
    const int row = get_local_id(0);
    const int col = get_local_id(1);
    const int globalRow = get_group_id(0) * TILE_SIZE + row;
    const int globalCol = get_group_id(1) * TILE_SIZE + col;

    __local float As[16][16];
    __local float Bs[16][16];

    float sum = 0.0f;

    for (int t = 0; t < (K + TILE_SIZE - 1) / TILE_SIZE; t++) {
        int tiledCol = t * TILE_SIZE + col;
        int tiledRow = t * TILE_SIZE + row;

        As[row][col] = (globalRow < M && tiledCol < K) ? A[globalRow * K + tiledCol] : 0.0f;
        Bs[row][col] = (tiledRow < K && globalCol < N) ? B[tiledRow * N + globalCol] : 0.0f;

        barrier(CLK_LOCAL_MEM_FENCE);

        for (int k = 0; k < TILE_SIZE; k++) {
            sum += As[row][k] * Bs[k][col];
        }

        barrier(CLK_LOCAL_MEM_FENCE);
    }

    if (globalRow < M && globalCol < N) {
        C[globalRow * N + globalCol] = alpha * sum + beta * C[globalRow * N + globalCol];
    }
}

// Softmax kernel for attention scores
__kernel void omni_softmax_f32(
    __global float* data,
    const int seq_len
) {
    const int row = get_global_id(0);
    const int offset = row * seq_len;

    // Find max
    float max_val = -INFINITY;
    for (int i = 0; i < seq_len; i++) {
        max_val = fmax(max_val, data[offset + i]);
    }

    // Exp and sum
    float sum = 0.0f;
    for (int i = 0; i < seq_len; i++) {
        data[offset + i] = exp(data[offset + i] - max_val);
        sum += data[offset + i];
    }

    // Normalize
    float inv_sum = 1.0f / sum;
    for (int i = 0; i < seq_len; i++) {
        data[offset + i] *= inv_sum;
    }
}

// GELU activation kernel
__kernel void omni_gelu_f32(__global float* data, const int n) {
    const int i = get_global_id(0);
    if (i < n) {
        float x = data[i];
        float cdf = 0.5f * (1.0f + tanh(0.7978845608f * (x + 0.044715f * x * x * x)));
        data[i] = x * cdf;
    }
}

// RMS normalization kernel
__kernel void omni_rmsnorm_f32(
    __global float* out,
    __global const float* x,
    __global const float* weight,
    const int n,
    const float eps
) {
    const int row = get_global_id(0);
    const int offset = row * n;

    float ss = 0.0f;
    for (int i = 0; i < n; i++) {
        ss += x[offset + i] * x[offset + i];
    }
    ss = 1.0f / sqrt(ss / (float)n + eps);

    for (int i = 0; i < n; i++) {
        out[offset + i] = x[offset + i] * ss * weight[i];
    }
}
