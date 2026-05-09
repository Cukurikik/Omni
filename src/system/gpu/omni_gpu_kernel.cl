// Omni GPU Kernel (OpenCL)
// Scientific & HPC Layer
// Extremely fast low-level parallel execution kernel for the SiLU (Swish) 
// activation function used in LLaMA-style architectures.

__kernel void omni_silu_activation(
    __global float* input,
    __global float* output,
    const unsigned int size
) {
    // Get global thread ID
    int id = get_global_id(0);

    // Bounds check
    if (id < size) {
        float x = input[id];
        // SiLU(x) = x * sigmoid(x)
        output[id] = x / (1.0f + exp(-x));
    }
}

// Fused kernel for RMSNorm (Root Mean Square Normalization)
__kernel void omni_rmsnorm(
    __global float* x,
    __global float* weight,
    __global float* output,
    const unsigned int hidden_dim,
    const float eps
) {
    int row = get_global_id(0); // Sequence index
    
    // Calculate sum of squares
    float ss = 0.0f;
    for(int i = 0; i < hidden_dim; i++) {
        float val = x[row * hidden_dim + i];
        ss += val * val;
    }
    
    // Calculate inverse root mean square
    ss /= (float)hidden_dim;
    ss += eps;
    float inv_rms = 1.0f / sqrt(ss);
    
    // Normalize and scale
    for(int i = 0; i < hidden_dim; i++) {
        output[row * hidden_dim + i] = x[row * hidden_dim + i] * inv_rms * weight[i];
    }
}
