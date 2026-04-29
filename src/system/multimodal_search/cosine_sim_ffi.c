#include <stdint.h>
#include <math.h>

extern "C" {

void omni_cosine_similarity(
    const double* vec_a, 
    const double* vec_b, 
    int32_t dim, 
    double* out_sim, 
    int32_t* err_code
) {
    if (!err_code) return;

    if (!vec_a || !vec_b || !out_sim || dim <= 0) {
        *err_code = -1;
        return;
    }

    double dot_product = 0.0;
    double norm_a = 0.0;
    double norm_b = 0.0;

    for (int32_t i = 0; i < dim; ++i) {
        double a = vec_a[i];
        double b = vec_b[i];
        
        dot_product += a * b;
        norm_a += a * a;
        norm_b += b * b;
    }

    if (norm_a == 0.0 || norm_b == 0.0) {
        *out_sim = 0.0;
    } else {
        *out_sim = dot_product / (sqrt(norm_a) * sqrt(norm_b));
    }

    *err_code = 0;
}

}
