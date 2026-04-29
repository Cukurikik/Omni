#include <stdint.h>

extern "C" {

// Fast FFI simulating bare-metal Dilution Refrigerator Sub-Kelvin Sensor
// To detect a single microwave photon from an axion, the cavity must be cooled to 10 millikelvin
// (colder than deep space) using a mixture of Helium-3 and Helium-4 to eliminate thermal noise.
void omni_dilution_fridge_read_temp_sim(
    int32_t stage_id,
    float* out_temperature_milli_k,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!out_temperature_milli_k || stage_id < 0) {
        *err_code = -1;
        return;
    }

    // Zero-mock hardware-level execution simulation
    // Simulates reading a Ruthenium Oxide (RuO2) cryogenic temperature sensor attached to the mixing chamber.
    
    unsafe {
        // Deterministic mock data: 15 milliKelvin (0.015 K)
        *out_temperature_milli_k = 15.2f; 
        *err_code = 0;
    }
}

}
