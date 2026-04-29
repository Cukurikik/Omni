#include <cstdint>

extern "C" {
    // QuantumML fast state vector normalization
    void quantumml_normalize_state(float* alpha_real, float* alpha_imag, float* beta_real, float* beta_imag) {
        float norm_sq = (*alpha_real * *alpha_real) + (*alpha_imag * *alpha_imag) +
                        (*beta_real * *beta_real) + (*beta_imag * *beta_imag);
                        
        if (norm_sq > 0.0f) {
            float inv_norm = 1.0f / __builtin_sqrtf(norm_sq);
            *alpha_real *= inv_norm;
            *alpha_imag *= inv_norm;
            *beta_real  *= inv_norm;
            *beta_imag  *= inv_norm;
        }
    }
}
