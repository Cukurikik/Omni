#include <cstdint>
#include <cmath>

extern "C" {

void omni_calculate_optical_flow(
    const double* frame_t1, 
    const double* frame_t2, 
    int32_t width, 
    int32_t height, 
    double* out_flow_x, 
    double* out_flow_y, 
    int32_t* err_code
) {
    if (!err_code) return;

    if (!frame_t1 || !frame_t2 || !out_flow_x || !out_flow_y || width <= 0 || height <= 0) {
        *err_code = -1;
        return;
    }

    // Deterministic mathematical implementation of simplified Horn-Schunck optical flow
    // calculating image gradients over time and space.
    
    for (int32_t y = 1; y < height - 1; ++y) {
        for (int32_t x = 1; x < width - 1; ++x) {
            int32_t idx = y * width + x;
            
            // Spatial gradients
            double Ix = (frame_t1[idx + 1] - frame_t1[idx - 1]) * 0.5;
            double Iy = (frame_t1[idx + width] - frame_t1[idx - width]) * 0.5;
            
            // Temporal gradient
            double It = frame_t2[idx] - frame_t1[idx];

            // Avoid division by zero
            double denominator = (Ix * Ix + Iy * Iy) + 1e-5;
            
            out_flow_x[idx] = -(Ix * It) / denominator;
            out_flow_y[idx] = -(Iy * It) / denominator;
        }
    }

    *err_code = 0;
}

}
