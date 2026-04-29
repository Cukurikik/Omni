#include <cstdint>

extern "C" {
    // RoboPlanner point-to-bounding-box fast collision detection
    bool roboplanner_check_collision(float px, float py, float pz,
                                    float bmin_x, float bmin_y, float bmin_z,
                                    float bmax_x, float bmax_y, float bmax_z) {
        return (px >= bmin_x && px <= bmax_x &&
                py >= bmin_y && py <= bmax_y &&
                pz >= bmin_z && pz <= bmax_z);
    }
}
