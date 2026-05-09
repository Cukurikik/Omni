//=============================================================================
// OMNI SYSTEM LAYER — CUDA ATTENTION MASKING (CUDA C++)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: Fast causal and padding mask generation kernels for Transformer 
//              attention mechanisms.
//=============================================================================

#include <cuda_runtime.h>
#include <math.h>

extern "C" {

#define BLOCK_SIZE 256

__global__ void causal_mask_kernel(float* mask, int seq_len, float fill_value) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    
    if (row < seq_len && col < seq_len) {
        // Causal masking: mask future tokens
        if (col > row) {
            mask[row * seq_len + col] = fill_value;
        } else {
            mask[row * seq_len + col] = 0.0f;
        }
    }
}

__global__ void apply_mask_kernel(float* scores, const float* mask, int batch_heads, int seq_len) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    int total_elements = batch_heads * seq_len * seq_len;
    
    if (idx < total_elements) {
        // Find which mask element this corresponds to
        int mask_idx = idx % (seq_len * seq_len);
        scores[idx] += mask[mask_idx];
    }
}

void omni_cuda_generate_causal_mask(float* d_mask, int seq_len, float fill_value) {
    dim3 threads(16, 16);
    dim3 blocks((seq_len + 15) / 16, (seq_len + 15) / 16);
    
    causal_mask_kernel<<<blocks, threads>>>(d_mask, seq_len, fill_value);
    cudaDeviceSynchronize();
}

void omni_cuda_apply_mask(float* d_scores, const float* d_mask, int batch_heads, int seq_len) {
    int total_elements = batch_heads * seq_len * seq_len;
    dim3 grid((total_elements + BLOCK_SIZE - 1) / BLOCK_SIZE);
    dim3 block(BLOCK_SIZE);
    
    apply_mask_kernel<<<grid, block>>>(d_scores, d_mask, batch_heads, seq_len);
    cudaDeviceSynchronize();
}

} // extern "C"
