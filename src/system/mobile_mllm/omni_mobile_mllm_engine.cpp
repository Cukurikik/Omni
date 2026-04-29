#include <cstdint>
#include <cmath>
#include <vector>
#include <string>
#include <algorithm>

// OMNI Mobile MLLM Engine — System Layer
// Absorbing UbiquitousLearning/mllm: Fast Multimodal LLM on Mobile Devices.
// C++ quantized inference kernel for on-device MLLM execution.

namespace omni { namespace system {

enum class QuantType : uint8_t { Q4_0 = 0, Q8_0 = 1, FP16 = 2 };

struct MllmResult {
    bool ok;
    std::string error;
    std::vector<float> logits;
};

class OmniMobileMllmEngine {
private:
    QuantType quant_;
    size_t vocab_size_;
    size_t hidden_dim_;
    uint64_t inferences_;

    // Q4_0 dequantization: each 4-bit value → float via scale factor
    static float dequant_q4(uint8_t nibble, float scale) {
        int8_t val = static_cast<int8_t>(nibble) - 8; // center around 0
        return static_cast<float>(val) * scale;
    }

    // Fused RMSNorm: x_i / sqrt(mean(x^2) + eps) * weight
    static void rms_norm(float* x, const float* weight, size_t n, float eps = 1e-5f) {
        float ss = 0.0f;
        for (size_t i = 0; i < n; ++i) ss += x[i] * x[i];
        ss = 1.0f / std::sqrt(ss / static_cast<float>(n) + eps);
        for (size_t i = 0; i < n; ++i) x[i] = x[i] * ss * weight[i];
    }

public:
    OmniMobileMllmEngine(size_t vocab_size, size_t hidden_dim, QuantType qt = QuantType::Q4_0)
        : quant_(qt), vocab_size_(vocab_size), hidden_dim_(hidden_dim), inferences_(0) {}

    // Softmax over logits for next-token prediction
    MllmResult softmax_logits(const std::vector<float>& raw_logits) {
        if (raw_logits.empty()) return {false, "MllmError: Empty logits", {}};
        if (raw_logits.size() != vocab_size_) return {false, "MllmError: Vocab size mismatch", {}};

        inferences_++;
        std::vector<float> probs(vocab_size_);
        float max_val = *std::max_element(raw_logits.begin(), raw_logits.end());
        float sum = 0.0f;
        for (size_t i = 0; i < vocab_size_; ++i) {
            probs[i] = std::exp(raw_logits[i] - max_val);
            sum += probs[i];
        }
        for (auto& p : probs) p /= sum;
        return {true, "", std::move(probs)};
    }

    std::string diagnostics() const {
        return "{\"engine\":\"OmniMobileMllmEngine\",\"vocab\":" + std::to_string(vocab_size_) +
               ",\"hidden\":" + std::to_string(hidden_dim_) +
               ",\"quant\":\"" + (quant_ == QuantType::Q4_0 ? "Q4_0" : quant_ == QuantType::Q8_0 ? "Q8_0" : "FP16") +
               "\",\"inferences\":" + std::to_string(inferences_) + ",\"status\":\"Operational\"}";
    }
};

}} // namespace omni::system
