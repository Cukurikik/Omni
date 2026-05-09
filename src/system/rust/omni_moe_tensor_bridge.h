#ifndef OMNI_MOE_TENSOR_BRIDGE_H
#define OMNI_MOE_TENSOR_BRIDGE_H

#include <stddef.h>

typedef struct {
    float* data;
    size_t length;
} OmniTensorView;

OmniTensorView omni_create_tensor_view(float* ptr, size_t len);

#endif
