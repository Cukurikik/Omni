#include <vector>
#include <string>
#include <numeric>

// Omni Fusion Bench Core (C++)
// Based on tanganke/fusion_bench
// Bare-metal tensor weight merging and evaluation.

struct FusionResult {
    bool success;
    std::vector<float> merged_weights;
    std::string error_msg;
};

class OmniFusionBench {
public:
    static FusionResult linear_weight_merge(const std::vector<float>& model_a, const std::vector<float>& model_b, float alpha) {
        if (model_a.empty() || model_b.empty() || model_a.size() != model_b.size()) {
            return {false, {}, "Model dimensions mismatch or empty"};
        }

        if (alpha < 0.0f || alpha > 1.0f) {
            return {false, {}, "Alpha must be between 0.0 and 1.0"};
        }

        std::vector<float> merged(model_a.size(), 0.0f);
        for (size_t i = 0; i < model_a.size(); ++i) {
            merged[i] = (alpha * model_a[i]) + ((1.0f - alpha) * model_b[i]);
        }

        return {true, merged, ""};
    }
};
