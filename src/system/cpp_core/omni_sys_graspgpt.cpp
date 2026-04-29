#include <cmath>

extern "C" {
    struct Vector3 {
        float x, y, z;
    };

    int omni_sys_graspgpt_check_collision(Vector3 point, Vector3* obstacles, float* radii, int obstacle_count) {
        if (obstacle_count < 0) return -1;

        for (int i = 0; i < obstacle_count; ++i) {
            float dx = point.x - obstacles[i].x;
            float dy = point.y - obstacles[i].y;
            float dz = point.z - obstacles[i].z;
            float dist_sq = dx*dx + dy*dy + dz*dz;
            
            if (dist_sq <= (radii[i] * radii[i])) {
                return 1; // Collision detected
            }
        }
        return 0; // No collision
    }
}
