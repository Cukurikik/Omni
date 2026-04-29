#include <stdbool.h>
#include <math.h>

#define MAX_VELOCITY 1000.0f
#define MIN_DT 0.001f

typedef struct {
    bool is_ok;
    float payload;
    const char* error;
} OmniResult_Float;

// Hard-bounded physics calculation for UniGoal environment
OmniResult_Float unigoal_compute_velocity(float current_v, float acceleration, float dt) {
    OmniResult_Float res = {0};
    
    if (dt < MIN_DT) {
        res.is_ok = false;
        res.error = "OMNI_MATH_ERR: dt too small, risk of numerical instability.";
        return res;
    }
    
    float new_v = current_v + (acceleration * dt);
    
    // Hard physics bounds
    if (new_v > MAX_VELOCITY) {
        new_v = MAX_VELOCITY;
    } else if (new_v < -MAX_VELOCITY) {
        new_v = -MAX_VELOCITY;
    }
    
    res.is_ok = true;
    res.payload = new_v;
    return res;
}

OmniResult_Float unigoal_compute_position(float current_p, float velocity, float dt) {
    OmniResult_Float res = {0};
    
    if (dt < MIN_DT) {
        res.is_ok = false;
        res.error = "OMNI_MATH_ERR: dt too small.";
        return res;
    }
    
    float new_p = current_p + (velocity * dt);
    
    res.is_ok = true;
    res.payload = new_p;
    return res;
}
