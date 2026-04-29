#include <cstdint>
#include <cmath>

extern "C" {

double omni_calculate_render_fps(int32_t polygon_count, int32_t resolution_x, int32_t resolution_y, int32_t* err_code) {
    if (!err_code) return 0.0;
    
    if (polygon_count <= 0 || resolution_x <= 0 || resolution_y <= 0) {
        *err_code = -1;
        return 0.0;
    }

    // Mathematical representation of Vulkan rendering performance
    double pixel_load = (double)(resolution_x * resolution_y) / 1000000.0;
    double poly_load = (double)polygon_count / 100000.0;
    
    double base_fps = 144.0;
    double performance_penalty = (pixel_load * 1.2) + (poly_load * 0.8);
    
    double final_fps = base_fps - performance_penalty;
    if (final_fps < 1.0) final_fps = 1.0;

    *err_code = 0;
    return final_fps;
}

}
