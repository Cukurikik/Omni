#ifndef OMNI_GEMM_BATCHED_CUH
#define OMNI_GEMM_BATCHED_CUH

#include <cuda_runtime.h>
#include <cuda_fp16.h>

// OMNI MOTHER: Batched GEMM for MoE Experts
extern "C" {

void omni_gemm_batched_f16(
    const half** A_array,
    const half** B_array,
    half** C_array,
    int m, int n, int k,
    int batch_count,
    cudaStream_t stream
);

}

#endif
