#include <cstdint>
#include <cstring>

extern "C" {

// Fast matrix subset extraction FFI simulating SHAP background dataset masking
void omni_extract_shap_subset(
    const float* background_dataset,
    int32_t num_samples,
    int32_t num_features,
    const int32_t* feature_mask, // 1 for keep feature, 0 for replace with background
    const float* target_instance,
    float* out_synthetic_dataset,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!background_dataset || !feature_mask || !target_instance || !out_synthetic_dataset) {
        *err_code = -1;
        return;
    }

    if (num_samples <= 0 || num_features <= 0) {
        *err_code = -2;
        return;
    }

    // Deterministically build synthetic instances for model evaluation
    for (int32_t i = 0; i < num_samples; ++i) {
        for (int32_t j = 0; j < num_features; ++j) {
            int32_t out_idx = i * num_features + j;
            
            if (feature_mask[j] == 1) {
                // Keep target instance feature
                out_synthetic_dataset[out_idx] = target_instance[j];
            } else {
                // Replace with background sample feature (marginalizing)
                out_synthetic_dataset[out_idx] = background_dataset[out_idx];
            }
        }
    }

    *err_code = 0;
}

}
