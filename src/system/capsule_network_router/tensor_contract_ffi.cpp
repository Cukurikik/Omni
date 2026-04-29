#include <stdint.h>

extern "C" {

// Fast FFI simulating tensor contraction for affine transformations in Capsule Networks (u_hat = W * u)
void omni_capsule_tensor_contract(
    const float* pose_matrices,
    const float* weight_matrices,
    int32_t batch_size,
    int32_t in_caps,
    int32_t out_caps,
    int32_t pose_dim,
    float* out_predictions,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!pose_matrices || !weight_matrices || !out_predictions || batch_size <= 0) {
        *err_code = -1;
        return;
    }

    // Zero-mock deterministic tensor contraction
    // Computing predictions for all out_caps from all in_caps
    for (int32_t b = 0; b < batch_size; ++b) {
        for (int32_t i = 0; i < in_caps; ++i) {
            for (int32_t j = 0; j < out_caps; ++j) {
                float sum = 0.0f;
                // Simplified 1D inner product for demonstration of affine transform
                for (int32_t d = 0; d < pose_dim; ++d) {
                    float pose = pose_matrices[b * in_caps * pose_dim + i * pose_dim + d];
                    float weight = weight_matrices[i * out_caps * pose_dim + j * pose_dim + d];
                    sum += pose * weight;
                }
                out_predictions[b * in_caps * out_caps + i * out_caps + j] = sum;
            }
        }
    }

    *err_code = 0;
}

}
