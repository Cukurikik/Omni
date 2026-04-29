#include <vector>
#include <stdexcept>
#include <iostream>

// OMNI PEFT: LoRA Weight Injection
// Low-level C++ simulation of applying Low-Rank Adaptation (LoRA) matrices to a frozen base weight tensor.
// Source: huggingface/peft

namespace omni::peft {

enum class LoraError {
    SUCCESS,
    DIMENSION_MISMATCH,
    NULL_PTR
};

template<typename T>
struct Result {
    T value;
    LoraError error;
    bool is_ok() const { return error == LoraError::SUCCESS; }
};

class LoraInjector {
public:
    /**
     * Applies W_new = W_base + (B * A) * (alpha / r)
     * W_base: [out_features, in_features]
     * A: [r, in_features]
     * B: [out_features, r]
     * All matrices are represented as flattened 1D arrays for simplicity.
     */
    static Result<bool> apply_lora_to_weight(
        float* w_base, 
        const float* lora_a, 
        const float* lora_b, 
        int in_features, 
        int out_features, 
        int r, 
        float alpha) 
    {
        if (!w_base || !lora_a || !lora_b) {
            return {false, LoraError::NULL_PTR};
        }

        if (r <= 0 || in_features <= 0 || out_features <= 0) {
            return {false, LoraError::DIMENSION_MISMATCH};
        }

        float scaling = alpha / (float)r;

        // Perform matrix multiplication: Delta_W = B * A
        // B is [out_features x r], A is [r x in_features]
        // Result is [out_features x in_features]
        
        for (int i = 0; i < out_features; ++i) {
            for (int j = 0; j < in_features; ++j) {
                float sum = 0.0f;
                for (int k = 0; k < r; ++k) {
                    float b_val = lora_b[i * r + k];
                    float a_val = lora_a[k * in_features + j];
                    sum += b_val * a_val;
                }
                
                // Add the scaled delta to the base weight
                w_base[i * in_features + j] += sum * scaling;
            }
        }

        return {true, LoraError::SUCCESS};
    }
};

} // namespace omni::peft
