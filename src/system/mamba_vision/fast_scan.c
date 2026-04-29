#include <stddef.h>

int fast_scan_1d(const float* input, float* output, size_t length) {
    if (!input || !output || length == 0) return -1;
    float sum = 0.0f;
    for (size_t i = 0; i < length; ++i) {
        sum += input[i];
        output[i] = sum;
    }
    return 0;
}
