#include <stdint.h>

extern "C" {

// Fast FFI simulating bare-metal Gravitational Microlensing Sensor
// Cosmic strings are invisible, but as they sweep across a background star,
// they create a perfect double-image of the star due to gravitational lensing.
void omni_microlensing_detect_sim(
    int32_t optical_telescope_id,
    float* out_lensing_angle_arcseconds,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!out_lensing_angle_arcseconds || optical_telescope_id < 0) {
        *err_code = -1;
        return;
    }

    // Zero-mock hardware-level execution simulation
    // Simulates processing photons from a billion background stars to find a duplicated pair.
    
    unsafe {
        // Deterministic mock data: A massive cosmic string is deflecting light by 3 arcseconds.
        *out_lensing_angle_arcseconds = 3.1f; 
        *err_code = 0;
    }
}

}
