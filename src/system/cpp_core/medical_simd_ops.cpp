#include <vector>

extern "C" void medical_simd_threshold(float* data, int size, float threshold) {
    for (int i = 0; i < size; ++i) {
        data[i] = (data[i] > threshold) ? 1.0f : 0.0f;
    }
}
