#include <cstdint>

extern "C" {
    // PanelGPT expert selection bounds checking
    uint32_t calculate_expert_quorum(uint32_t num_experts, float reliability_threshold) {
        if (num_experts == 0) return 0;
        uint32_t required = static_cast<uint32_t>(num_experts * reliability_threshold);
        return required == 0 ? 1 : required;
    }

    float average_panel_confidence(const float* confidences, uint32_t count) {
        if (count == 0) return 0.0f;
        float sum = 0.0f;
        for (uint32_t i = 0; i < count; ++i) {
            sum += confidences[i];
        }
        return sum / count;
    }
}
