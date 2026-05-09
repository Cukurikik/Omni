#ifndef OMNI_ADATT_KERNELS_CUH
#define OMNI_ADATT_KERNELS_CUH

#include <cuda_runtime.h>

extern "C" {
void omni_adatt_fuse(const float* in, float* out, const float* weights, int tasks, int dim, cudaStream_t stream);
}

#endif
