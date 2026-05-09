// OMNI System Layer — CUDA Kernel Launcher
// Entry point for launching GPU kernels from Python/C++ FFI.

#include "attention_kernel.cuh"
#include "gemm_kernel.cuh"
#include <cstdio>

extern "C" {

// Launch tiled attention
void omni_attention_forward(
    const float* Q, const float* K, const float* V, float* O,
    int batch_size, int num_heads, int seq_len_q, int seq_len_k,
    int head_dim, float scale, int causal, cudaStream_t stream
) {
    omni::system::attention::AttentionKernelConfig cfg;
    cfg.batch_size = batch_size;
    cfg.num_heads = num_heads;
    cfg.seq_len_q = seq_len_q;
    cfg.seq_len_k = seq_len_k;
    cfg.head_dim = head_dim;
    cfg.scale = scale;
    cfg.causal = (causal != 0);
    cfg.block_size_q = 32;
    cfg.block_size_k = 32;

    omni::system::attention::launch_tiled_attention(Q, K, V, O, cfg, stream);
}

// Launch GEMM
void omni_gemm(
    const float* A, const float* B, float* C,
    int M, int N, int K,
    float alpha, float beta, cudaStream_t stream
) {
    omni::system::gemm::launch_gemm(A, B, C, M, N, K, alpha, beta, stream);
}

// Launch fused GEMM + GELU
void omni_gemm_gelu(
    const float* A, const float* B, float* C,
    int M, int N, int K, cudaStream_t stream
) {
    omni::system::gemm::launch_gemm_gelu(A, B, C, M, N, K, stream);
}

}  // extern "C"
