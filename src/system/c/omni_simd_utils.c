// OMNI System — C SIMD Fallback Utilities
// Provides baseline SIMD routines if AVX-512 is not available

#include <stdint.h>
#include <stddef.h>
#include <math.h>

// Fallback scalar implementation of Gelu activation
void omni_gelu_fallback(float* data, size_t length) {
    const float SQRT_2_OVER_PI = 0.7978845608028654f;
    const float COEF = 0.044715f;
    
    for (size_t i = 0; i < length; i++) {
        float x = data[i];
        float x3 = x * x * x;
        float tanh_arg = SQRT_2_OVER_PI * (x + COEF * x3);
        data[i] = 0.5f * x * (1.0f + tanhf(tanh_arg));
    }
}

// Fallback scalar implementation of Softmax
void omni_softmax_fallback(float* data, size_t length) {
    float max_val = data[0];
    for (size_t i = 1; i < length; i++) {
        if (data[i] > max_val) max_val = data[i];
    }
    
    float sum = 0.0f;
    for (size_t i = 0; i < length; i++) {
        data[i] = expf(data[i] - max_val);
        sum += data[i];
    }
    
    for (size_t i = 0; i < length; i++) {
        data[i] /= sum;
    }
}
