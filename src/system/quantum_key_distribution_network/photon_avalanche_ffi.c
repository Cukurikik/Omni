#include <stdint.h>

extern "C" {

// Fast FFI simulating bare-metal Single-Photon Avalanche Diode (SPAD)
// We need to detect individual photons to read the quantum state (polarization).
// SPADs operate above the breakdown voltage (Geiger mode) to trigger an avalanche
// of electrons from a single photon strike.
void omni_detect_single_photon_sim(
    int32_t sensor_array_id,
    int32_t* out_photon_detected,
    float* out_polarization_angle,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!out_photon_detected || !out_polarization_angle || sensor_array_id < 0) {
        *err_code = -1;
        return;
    }

    // Zero-mock hardware-level execution simulation
    // Simulates reading the avalanche current and resolving the polarization filter.
    
    unsafe {
        // Deterministic mock data: Photon detected at 45 degrees (Diagonal basis)
        *out_photon_detected = 1; 
        *out_polarization_angle = 45.0f; 
        *err_code = 0;
    }
}

}
