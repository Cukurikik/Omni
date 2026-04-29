#include <cstdint>

extern "C" {

void omni_initialize_tensors(
    double* tensor_data, 
    int32_t num_entities, 
    int32_t dim, 
    double init_scale, 
    int32_t* err_code
) {
    if (!err_code) return;

    if (!tensor_data || num_entities <= 0 || dim <= 0) {
        *err_code = -1;
        return;
    }

    // Deterministic pseudo-random initialization (Xavier-like) without OS entropy
    // To ensure reproducible training runs
    for (int i = 0; i < num_entities; ++i) {
        for (int j = 0; j < dim; ++j) {
            // Chaotic map math for deterministic distribution
            double val = ((double)((i * 31 + j * 17) % 1000) / 1000.0) * 2.0 - 1.0;
            tensor_data[i * dim + j] = val * init_scale;
        }
    }

    *err_code = 0;
}

}
