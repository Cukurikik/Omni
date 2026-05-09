// OMNI Scientific & HPC Layer
// OpenCL Kernel for accelerating matrix operations on cross-vendor GPUs (AMD, Intel, Nvidia)
// Directly maps to the universal binary fallback layers when CUDA is unavailable.

__kernel void omni_matrix_multiply(
    const int M,
    const int N,
    const int K,
    const __global float* A,
    const __global float* B,
    __global float* C) 
{
    // Thread identifiers
    const int globalRow = get_global_id(0); // Row ID of C (0..M)
    const int globalCol = get_global_id(1); // Col ID of C (0..N)

    if (globalRow < M && globalCol < N) {
        float acc = 0.0f;
        
        // Compute dot product for C[globalRow][globalCol]
        for (int k = 0; k < K; k++) {
            // A is M x K, B is K x N
            acc += A[globalRow * K + k] * B[k * N + globalCol];
        }
        
        C[globalRow * N + globalCol] = acc;
    }
}

__kernel void omni_gelu_activation(
    const int N,
    __global float* X)
{
    const int i = get_global_id(0);
    
    if (i < N) {
        float x = X[i];
        // GELU Approximation: 0.5 * x * (1 + tanh(sqrt(2/pi) * (x + 0.044715 * x^3)))
        float val = 0.5f * x * (1.0f + tanh(0.7978845608f * (x + 0.044715f * x * x * x)));
        X[i] = val;
    }
}
