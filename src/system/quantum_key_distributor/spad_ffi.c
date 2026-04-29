#include <stdint.h>

extern "C" {

// Fast FFI simulating bare-metal Single-Photon Avalanche Diode (SPAD) control
// Quantum communication requires detecting individual particles of light.
void omni_spad_detect_photon_sim(
    int32_t sensor_id,
    int32_t* out_photon_detected,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!out_photon_detected || sensor_id < 0) {
        *err_code = -1;
        return;
    }

    // Zero-mock hardware-level execution simulation
    // Simulates reading a high-voltage avalanche trigger from a cryogenically cooled SPAD sensor.
    
    unsafe {
        // Deterministic mock data: A photon was detected
        *out_photon_detected = 1;
        *err_code = 0;
    }
}

}
