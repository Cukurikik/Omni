// @omni-layer Scientific | @omni-lang OpenCL | @omni-batch 17
// @omni-description OpenCL GEMM kernel: portable GPU matrix multiply
// for cross-vendor inference acceleration (NVIDIA/AMD/Intel).

__kernel void omni_gemm_f32(
    __global const float* A,
    __global const float* B,
    __global float* C,
    const int M, const int N, const int K
) {
    const int row = get_global_id(0);
    const int col = get_global_id(1);
    if (row >= M || col >= N) return;

    float sum = 0.0f;
    for (int k = 0; k < K; k++) {
        sum += A[row * K + k] * B[k * N + col];
    }
    C[row * N + col] = sum;
}

__kernel void omni_gemm_tiled(
    __global const float* A,
    __global const float* B,
    __global float* C,
    const int M, const int N, const int K,
    __local float* tileA,
    __local float* tileB
) {
    const int TILE = 16;
    const int row = get_global_id(0);
    const int col = get_global_id(1);
    const int lr = get_local_id(0);
    const int lc = get_local_id(1);
    float sum = 0.0f;

    for (int t = 0; t < (K + TILE - 1) / TILE; t++) {
        int aCol = t * TILE + lc;
        int bRow = t * TILE + lr;
        tileA[lr * TILE + lc] = (row < M && aCol < K) ? A[row * K + aCol] : 0.0f;
        tileB[lr * TILE + lc] = (bRow < K && col < N) ? B[bRow * N + col] : 0.0f;
        barrier(CLK_LOCAL_MEM_FENCE);
        for (int k = 0; k < TILE; k++) {
            sum += tileA[lr * TILE + k] * tileB[k * TILE + lc];
        }
        barrier(CLK_LOCAL_MEM_FENCE);
    }
    if (row < M && col < N) C[row * N + col] = sum;
}

__kernel void omni_softmax_f32(
    __global float* data,
    const int n
) {
    const int gid = get_global_id(0);
    const int row_start = gid * n;
    float max_val = data[row_start];
    for (int i = 1; i < n; i++) {
        max_val = fmax(max_val, data[row_start + i]);
    }
    float sum = 0.0f;
    for (int i = 0; i < n; i++) {
        data[row_start + i] = exp(data[row_start + i] - max_val);
        sum += data[row_start + i];
    }
    for (int i = 0; i < n; i++) {
        data[row_start + i] /= (sum + 1e-8f);
    }
}

__kernel void omni_relu_f32(__global float* data, const int n) {
    const int i = get_global_id(0);
    if (i < n) data[i] = fmax(0.0f, data[i]);
}

__kernel void omni_layer_norm_f32(
    __global float* data, const int n, const float eps
) {
    const int gid = get_global_id(0);
    const int start = gid * n;
    float mean = 0.0f;
    for (int i = 0; i < n; i++) mean += data[start + i];
    mean /= (float)n;
    float var = 0.0f;
    for (int i = 0; i < n; i++) {
        float d = data[start + i] - mean;
        var += d * d;
    }
    var /= (float)n;
    float inv_std = 1.0f / sqrt(var + eps);
    for (int i = 0; i < n; i++) {
        data[start + i] = (data[start + i] - mean) * inv_std;
    }
}
