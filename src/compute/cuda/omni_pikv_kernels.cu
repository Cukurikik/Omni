#include "omni_pikv_kernels.cuh"

// OMNI MOTHER: PiKV Paged Attention & Cache Kernels
// Accelerates physical to virtual block mapping

__global__ void omni_pikv_write_cache_kernel(
    const half* key_states,
    const half* value_states,
    half* key_cache,
    half* value_cache,
    const int* block_table,
    int seq_len,
    int head_dim,
    int block_size
) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    
    // Virtual sequence index
    int seq_idx = tid / head_dim;
    int dim_idx = tid % head_dim;
    
    if (seq_idx < seq_len) {
        int logical_block = seq_idx / block_size;
        int physical_block = block_table[logical_block];
        int block_offset = seq_idx % block_size;
        
        int physical_idx = (physical_block * block_size + block_offset) * head_dim + dim_idx;
        
        key_cache[physical_idx] = key_states[tid];
        value_cache[physical_idx] = value_states[tid];
    }
}

extern "C" {
void omni_pikv_write_cache(
    const half* k, const half* v,
    half* k_cache, half* v_cache,
    const int* block_table,
    int seq_len, int head_dim, int block_size,
    cudaStream_t stream
) {
    int total_threads = seq_len * head_dim;
    int blocks = (total_threads + 255) / 256;
    omni_pikv_write_cache_kernel<<<blocks, 256, 0, stream>>>(
        k, v, k_cache, v_cache, block_table, seq_len, head_dim, block_size
    );
}
}
