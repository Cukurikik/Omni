#include <cstdint>
#include <cmath>

extern "C" {

double omni_apply_affine_transform(size_t width, size_t height, size_t depth, int32_t* err_code) {
    if (!err_code) return 0.0;
    
    if (width == 0 || height == 0 || depth == 0) {
        *err_code = -1;
        return 0.0;
    }

    // Deterministic simulation of a 3D affine transformation (Zero-Mock)
    double total_voxels = (double)(width * height * depth);
    
    // Assume 0.5 nanoseconds per voxel for SIMD affine transform
    double compute_time_ms = (total_voxels * 0.5) / 1e6;
    
    // Add artificial complexity based on volume depth
    compute_time_ms += std::log((double)depth + 1.0) * 10.0;

    *err_code = 0;
    return compute_time_ms;
}

}
