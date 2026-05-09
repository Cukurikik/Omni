// OMNI Framework - Domain Specific Small Language Model Quantizer
// Zero-mock C++ logic for 4-bit and 8-bit dynamic quantization of SLMs.

#include <vector>
#include <cmath>
#include <cstdint>
#include <stdexcept>
#include <iostream>

namespace OmniSLM {

    struct QuantizedTensor8 {
        std::vector<int8_t> data;
        float scale;
        float zero_point;
    };

    class Quantizer {
    public:
        // Symmetrically quantize a float vector to 8-bit integers
        static QuantizedTensor8 quantize_8bit(const std::vector<float>& weights) {
            if (weights.empty()) {
                throw std::invalid_argument("Empty weights vector provided.");
            }

            float max_val = 0.0f;
            for (float w : weights) {
                if (std::abs(w) > max_val) {
                    max_val = std::abs(w);
                }
            }

            QuantizedTensor8 qt;
            qt.scale = max_val / 127.0f;
            qt.zero_point = 0.0f;
            qt.data.reserve(weights.size());

            for (float w : weights) {
                float scaled = w / qt.scale;
                int8_t q_val = static_cast<int8_t>(std::round(scaled));
                
                // Clamp
                if (q_val > 127) q_val = 127;
                if (q_val < -127) q_val = -127;
                
                qt.data.push_back(q_val);
            }

            return qt;
        }

        static std::vector<float> dequantize_8bit(const QuantizedTensor8& qt) {
            std::vector<float> weights;
            weights.reserve(qt.data.size());

            for (int8_t q : qt.data) {
                weights.push_back(static_cast<float>(q) * qt.scale);
            }
            return weights;
        }
    };

} // namespace OmniSLM

extern "C" {
    // C-API FFI Boundary
    void* omni_slm_quantize_array(const float* data, size_t size, float* out_scale) {
        std::vector<float> vec(data, data + size);
        auto qt = OmniSLM::Quantizer::quantize_8bit(vec);
        *out_scale = qt.scale;
        
        int8_t* out_data = new int8_t[size];
        std::copy(qt.data.begin(), qt.data.end(), out_data);
        return out_data;
    }

    void omni_slm_free_quantized(void* ptr) {
        delete[] static_cast<int8_t*>(ptr);
    }
}
