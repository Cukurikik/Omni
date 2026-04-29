#include <cmath>

extern "C" {
    float omni_sys_oceangym_water_resistance(float velocity) {
        // Drag equation mock: F_d = 0.5 * rho * v^2 * C_d * A
        float rho = 1025.0f; // Density of sea water kg/m^3
        float c_d_a = 0.04f; // Drag coefficient * area mock
        
        float drag = 0.5f * rho * velocity * velocity * c_d_a;
        return (velocity >= 0.0f) ? -drag : drag;
    }
}
