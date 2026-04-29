#include <stdlib.h>

typedef struct {
    float* reduced_grads;
    const char* error;
    int is_ok;
} OmniResultReducer;

OmniResultReducer apply_gradient_reduction(float* grads, float* momentum, int size, float lr) {
    if (!grads || !momentum || size <= 0) {
        return (OmniResultReducer){NULL, "Invalid inputs", 0};
    }
    
    float* out = (float*)malloc(size * sizeof(float));
    if (!out) return (OmniResultReducer){NULL, "OOM", 0};
    
    for (int i = 0; i < size; i++) {
        momentum[i] = 0.9f * momentum[i] + 0.1f * grads[i];
        out[i] = -lr * momentum[i];
    }
    
    return (OmniResultReducer){out, NULL, 1};
}
