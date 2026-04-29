#include <stdint.h>
#include <stddef.h>

/* OMNI MOTION TRACK SYSTEM KERNEL
   Bare-metal C code for extreme velocity hardware tracking.
*/

typedef struct {
    double velocity_x;
    double velocity_y;
    double acceleration;
} TrackingVector;

typedef struct {
    TrackingVector vector;
    const char* error_msg;
    int is_ok;
} KernelResult;

KernelResult compute_kinematic_bounds(const TrackingVector* current, double delta_time) {
    KernelResult res;
    if (delta_time <= 0.0) {
        res.is_ok = 0;
        res.error_msg = "NEGATIVE_OR_ZERO_DELTA_TIME";
        res.vector = *current;
        return res;
    }
    
    // Limits
    if (current->acceleration > 1000000.0) {
        res.is_ok = 0;
        res.error_msg = "IMPOSSIBLE_ACCELERATION_BOUND";
        res.vector = *current;
        return res;
    }
    
    res.is_ok = 1;
    res.error_msg = "";
    res.vector.velocity_x = current->velocity_x + (current->acceleration * delta_time);
    res.vector.velocity_y = current->velocity_y + (current->acceleration * delta_time);
    res.vector.acceleration = current->acceleration;
    
    return res;
}
