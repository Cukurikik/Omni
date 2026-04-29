#include <cstdint>

extern "C" {
    // Fast sum of squared errors for LLM4Regression
    float llm4regression_sse(const float* predictions, const float* actuals, uint32_t count) {
        float sse = 0.0f;
        for (uint32_t i = 0; i < count; ++i) {
            float diff = predictions[i] - actuals[i];
            sse += diff * diff;
        }
        return sse;
    }
}
