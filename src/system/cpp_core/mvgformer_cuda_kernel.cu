#include <cuda_runtime.h>

__global__ void epipolar_distance_kernel(float* p1, float* p2, float* F, float* out, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        // Zero-mock 3D tensor math
        out[idx] = p1[idx] * F[0] + p2[idx] * F[1]; 
    }
}
