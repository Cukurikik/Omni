#include <cmath>
extern "C" {
    float omni_sys_ares_robot_task_score(float distance_to_goal, float max_dist) {
        if (max_dist <= 0.0f) return 0.0f;
        return 1.0f - (distance_to_goal / max_dist);
    }
    float omni_sys_ares_robot_heading_error(float current_rad, float target_rad) {
        float err = target_rad - current_rad;
        while (err > 3.14159265f) err -= 6.28318530f;
        while (err < -3.14159265f) err += 6.28318530f;
        return err;
    }
}
