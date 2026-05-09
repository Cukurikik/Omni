#ifndef OMNI_PIKV_KERNELS_CUH
#define OMNI_PIKV_KERNELS_CUH

#include <cuda_runtime.h>
#include <cuda_fp16.h>

extern "C" {
void omni_pikv_write_cache(
    const half* k, const half* v,
    half* k_cache, half* v_cache,
    const int* block_table,
    int seq_len, int head_dim, int block_size,
    cudaStream_t stream
);
}

#endif
