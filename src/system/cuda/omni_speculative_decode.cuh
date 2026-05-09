#ifndef OMNI_SPECULATIVE_DECODE_CUH
#define OMNI_SPECULATIVE_DECODE_CUH

#include <cuda_runtime.h>

extern "C" {
void omni_run_speculative_verification(const int* draft, const float* logits, int* count, int len, cudaStream_t stream);
}

#endif
