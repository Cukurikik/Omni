#ifndef OMNI_MOE_SCATTER_CUH
#define OMNI_MOE_SCATTER_CUH
#include <cuda_runtime.h>

extern "C" {
void omni_moe_scatter(const float* in, float* out, const int* idx, int tokens, int dim, cudaStream_t stream);
}

#endif
