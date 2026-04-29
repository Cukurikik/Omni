#include <cstdint>
#include <cmath>

extern "C" {

void omni_update_environment_physics(
    const double* positions,
    const double* velocities,
    const double* forces,
    int32_t num_entities,
    double dt,
    double* out_positions,
    double* out_velocities,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!positions || !velocities || !forces || !out_positions || !out_velocities || num_entities <= 0 || dt <= 0) {
        *err_code = -1;
        return;
    }

    // Deterministic mathematical implementation of Symplectic Euler Integration
    // commonly used in continuous RL environments for numerical stability
    
    double mass = 1.0; // Normalized mass

    for (int i = 0; i < num_entities; ++i) {
        // 1. Update velocity: v(t+dt) = v(t) + (F/m) * dt
        double acceleration = forces[i] / mass;
        out_velocities[i] = velocities[i] + acceleration * dt;
        
        // Apply deterministic friction
        out_velocities[i] *= 0.99;

        // 2. Update position: x(t+dt) = x(t) + v(t+dt) * dt
        out_positions[i] = positions[i] + out_velocities[i] * dt;
        
        // Deterministic bounds clamping (World boundaries [-100, 100])
        if (out_positions[i] > 100.0) {
            out_positions[i] = 100.0;
            out_velocities[i] *= -0.5; // Bounce
        } else if (out_positions[i] < -100.0) {
            out_positions[i] = -100.0;
            out_velocities[i] *= -0.5;
        }
    }

    *err_code = 0;
}

}
