#include <cstdint>
#include <cmath>

extern "C" {

void omni_calculate_transe_distance(
    const double* head, 
    const double* relation, 
    const double* tail, 
    int32_t dim, 
    double* out_distance, 
    int32_t* err_code
) {
    if (!err_code) return;

    if (!head || !relation || !tail || !out_distance || dim <= 0) {
        *err_code = -1;
        return;
    }

    // TransE Score Function: || h + r - t || (L2 norm)
    double distance = 0.0;
    
    for (int32_t i = 0; i < dim; ++i) {
        double diff = (head[i] + relation[i]) - tail[i];
        distance += diff * diff;
    }
    
    *out_distance = std::sqrt(distance);
    *err_code = 0;
}

}
