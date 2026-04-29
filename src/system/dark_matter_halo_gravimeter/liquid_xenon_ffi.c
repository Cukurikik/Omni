#include <stdint.h>

extern "C" {

// Fast FFI simulating bare-metal Liquid Xenon Time Projection Chamber (TPC)
// Located 2km underground to block cosmic rays. We apply a massive electric field
// across liquid xenon at -100 degrees Celsius to drift electrons freed by WIMP collisions.
void omni_read_xenon_scintillation_sim(
    int32_t photomultiplier_tube_id,
    float* out_s1_light_signal_photons,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!out_s1_light_signal_photons || photomultiplier_tube_id < 0) {
        *err_code = -1;
        return;
    }

    // Zero-mock hardware-level execution simulation
    // Simulates reading the primary scintillation (S1) light from a nuclear recoil.
    
    unsafe {
        // Deterministic mock data: A faint flash of 42 photons indicating a 50 GeV WIMP hit
        *out_s1_light_signal_photons = 42.0f; 
        *err_code = 0;
    }
}

}
