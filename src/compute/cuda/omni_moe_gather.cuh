#ifndef OMNI_MOE_GATHER_CUH
#define OMNI_MOE_GATHER_CUH
#include <cuda_runtime.h>

extern "C" {
void omni_moe_gather(const float* in, float* out, const int* idx, int tokens, int dim, cudaStream_t stream);
}

#endif
