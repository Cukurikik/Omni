#ifndef OMNI_FLASH_ATTENTION_CUH
#define OMNI_FLASH_ATTENTION_CUH

#include <cuda_runtime.h>
#include <cuda_fp16.h>

// OMNI MOTHER: Flash Attention V3 CUDA bindings
// Implements Hopper-optimized TMA (Tensor Memory Accelerator) asynchronous copies
// for extreme long-context MoE inference sequences.

extern "C" {

void omni_flash_attention_v3_forward_f16(
    const half* q, 
    const half* k, 
    const half* v, 
    half* out,
    int batch_size,
    int seq_len,
    int num_heads,
    int head_dim,
    float softmax_scale,
    cudaStream_t stream
);

}

#endif // OMNI_FLASH_ATTENTION_CUH
