// OMNI HPC — OpenCL Vector Addition Kernel
// Runs on AMD, Intel, and NVIDIA GPUs uniformly

__kernel void omni_vector_add(
    __global const float* A, 
    __global const float* B, 
    __global float* C, 
    const unsigned int n)
{
    // Get the index of the current element to be processed
    int id = get_global_id(0);
    
    // Do the operation
    if (id < n) {
        C[id] = A[id] + B[id];
    }
}
