#include <cmath>
#include <vector>
#include <algorithm>
#include <cstdint>

extern "C" {
    // 8-bit MinMax Quantization typical in LLM bitsandbytes optimization
    void omni_quantize_8bit(const float* input, int8_t* output, float* scale, size_t n) {
        float max_val = 0.0f;
        for (size_t i = 0; i < n; ++i) {
            float abs_val = std::abs(input[i]);
            if (abs_val > max_val) max_val = abs_val;
        }

        *scale = max_val / 127.0f;
        float inv_scale = (*scale == 0.0f) ? 0.0f : 1.0f / *scale;

        for (size_t i = 0; i < n; ++i) {
            float scaled = input[i] * inv_scale;
            scaled = std::max(-128.0f, std::min(127.0f, std::round(scaled)));
            output[i] = static_cast<int8_t>(scaled);
        }
    }
}
