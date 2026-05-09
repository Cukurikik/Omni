#ifndef OMNI_QWEN2_MOE_CPP_H
#define OMNI_QWEN2_MOE_CPP_H

// OMNI MOTHER: qwen2.cpp Port Header

namespace omni {
namespace qwen2 {

void qwen2_moe_forward(const float* input, float* output, const float* expert_weights, int seq_len, int hidden_dim, int num_experts);

}
}

#endif
