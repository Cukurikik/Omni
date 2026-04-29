#include <cstdint>
#include <vector>

extern "C" {

void omni_compute_blendshapes(
    const double* base_mesh, 
    const double* blendshape_deltas, 
    const double* coefficients, 
    int32_t num_vertices, 
    int32_t num_shapes, 
    double* out_mesh, 
    int32_t* err_code
) {
    if (!err_code) return;

    if (!base_mesh || !blendshape_deltas || !coefficients || !out_mesh || num_vertices <= 0 || num_shapes <= 0) {
        *err_code = -1;
        return;
    }

    // Initialize with base mesh
    int32_t total_coords = num_vertices * 3; // 3D coordinates
    for (int32_t i = 0; i < total_coords; ++i) {
        out_mesh[i] = base_mesh[i];
    }

    // Deterministic mathematical tensor accumulation for blendshapes
    // out = base + sum_k (coef_k * delta_k)
    for (int32_t k = 0; k < num_shapes; ++k) {
        double coef = coefficients[k];
        
        // Skip if coefficient is essentially zero (performance optimization, mathematically sound)
        if (coef > -1e-6 && coef < 1e-6) continue;

        int32_t shape_offset = k * total_coords;
        for (int32_t i = 0; i < total_coords; ++i) {
            out_mesh[i] += coef * blendshape_deltas[shape_offset + i];
        }
    }

    *err_code = 0;
}

}
