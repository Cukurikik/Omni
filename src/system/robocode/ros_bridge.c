#include <stdbool.h>
#include <string.h>

typedef struct {
    void* value;
    const char* error;
    bool is_ok;
} OmniResult;

typedef struct {
    double x;
    double y;
    double theta;
} Twist;

OmniResult publish_cmd_vel(Twist cmd) {
    // C-based ROS bridge for RoboCode
    if (cmd.x > 5.0 || cmd.x < -5.0) {
        return (OmniResult){.value = NULL, .error = "Velocity out of bounds", .is_ok = false};
    }
    
    // Publish simulated memory write
    static Twist current_velocity;
    current_velocity = cmd;
    
    return (OmniResult){.value = &current_velocity, .error = NULL, .is_ok = true};
}
