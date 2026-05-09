//=============================================================================
// OMNI SYSTEM LAYER — CUDA LOSS FUNCTIONS (CUDA C++)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: Hardware-accelerated loss functions for training/fine-tuning 
//              models within the Omni compute ecosystem.
//=============================================================================

#include <cuda_runtime.h>
#include <math.h>

extern "C" {

#define BLOCK_SIZE 256

__global__ void cross_entropy_loss_kernel(
    float* loss_out, const float* logits, const int* targets, 
    int batch_size, int num_classes
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    
    if (idx < batch_size) {
        int target_class = targets[idx];
        const float* sample_logits = logits + (idx * num_classes);
        
        // 1. Find max for numerical stability
        float max_logit = -1e20f;
        for (int c = 0; c < num_classes; ++c) {
            if (sample_logits[c] > max_logit) {
                max_logit = sample_logits[c];
            }
        }
        
        // 2. Compute sum of exp
        float sum_exp = 0.0f;
        for (int c = 0; c < num_classes; ++c) {
            sum_exp += expf(sample_logits[c] - max_logit);
        }
        
        // 3. Compute loss: -log(exp(logit[target]) / sum_exp)
        float log_prob = (sample_logits[target_class] - max_logit) - logf(sum_exp);
        loss_out[idx] = -log_prob;
    }
}

void omni_cuda_execute_cross_entropy(
    float* d_loss_out, const float* d_logits, const int* d_targets, 
    int batch_size, int num_classes
) {
    dim3 grid((batch_size + BLOCK_SIZE - 1) / BLOCK_SIZE);
    dim3 block(BLOCK_SIZE);
    
    cross_entropy_loss_kernel<<<grid, block>>>(d_loss_out, d_logits, d_targets, batch_size, num_classes);
    cudaDeviceSynchronize();
}

} // extern "C"
