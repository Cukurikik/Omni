#include <stdint.h>

extern "C" {

// Fast FFI simulating SHAP (SHapley Additive exPlanations) value aggregation
// Used in Responsible AI Toolbox for Model Interpretability
void omni_shapley_aggregation(
    const float* local_shap_values,
    int32_t num_samples,
    int32_t num_features,
    float* out_global_importance,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!local_shap_values || !out_global_importance || num_samples <= 0 || num_features <= 0) {
        *err_code = -1;
        return;
    }

    // Zero-mock deterministic absolute mean aggregation
    // Global feature importance is the mean absolute SHAP value across all samples
    for (int32_t f = 0; f < num_features; ++f) {
        float sum_abs = 0.0f;
        for (int32_t s = 0; s < num_samples; ++s) {
            float val = local_shap_values[s * num_features + f];
            if (val < 0.0f) val = -val;
            sum_abs += val;
        }
        out_global_importance[f] = sum_abs / (float)num_samples;
    }

    *err_code = 0;
}

}
