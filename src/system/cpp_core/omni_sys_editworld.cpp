#include <cstdint>

extern "C" {
    int omni_sys_editworld_bounds(float x, float y, float bounds_x, float bounds_y) {
        if (x < 0.0f || x > bounds_x) return 0; // Out of bounds X
        if (y < 0.0f || y > bounds_y) return 0; // Out of bounds Y
        return 1; // Within bounds
    }
}
