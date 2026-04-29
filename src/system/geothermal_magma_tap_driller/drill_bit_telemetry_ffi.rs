#include <stdint.h>

extern "C" {

// Fast FFI simulating bare-metal Tungsten Carbide Drill Bit Telemetry
// At 10km depth and 900°C, normal electronics melt. We use specialized high-temperature
// acoustic sensors that send data back to the surface via sound pulses through the steel drill pipe.
void omni_drill_bit_read_temp_sim(
    int32_t bit_id,
    float* out_temperature_c,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!out_temperature_c || bit_id < 0) {
        *err_code = -1;
        return;
    }

    // Zero-mock hardware-level execution simulation
    // Simulates reading temperature from a Measurement While Drilling (MWD) tool.
    
    unsafe {
        // Deterministic mock data: Approaching the magma chamber
        *out_temperature_c = 850.5f; 
        *err_code = 0;
    }
}

}
