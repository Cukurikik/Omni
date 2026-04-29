#include <cstdint>

extern "C" {
    float omni_sys_easyrec_dot(const float* vec_a, const float* vec_b, int dim) {
        if (dim <= 0 || !vec_a || !vec_b) return 0.0f;
        
        float result = 0.0f;
        // Unrolled for performance
        int i = 0;
        for (; i <= dim - 4; i += 4) {
            result += vec_a[i] * vec_b[i] +
                      vec_a[i+1] * vec_b[i+1] +
                      vec_a[i+2] * vec_b[i+2] +
                      vec_a[i+3] * vec_b[i+3];
        }
        for (; i < dim; ++i) {
            result += vec_a[i] * vec_b[i];
        }
        return result;
    }
}
