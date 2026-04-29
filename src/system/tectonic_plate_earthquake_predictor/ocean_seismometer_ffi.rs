#include <stdint.h>

extern "C" {

// Fast FFI simulating bare-metal Ocean-Bottom Seismometer (OBS) Acoustic Telemetry
// To detect subduction zone earthquakes early (like the Cascadia fault), sensors are dropped
// 3 kilometers deep onto the ocean floor. They transmit data back up to buoys using acoustic modems.
void omni_obs_read_hydrophone_sim(
    int32_t station_id,
    float* out_vertical_acceleration_g,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!out_vertical_acceleration_g || station_id < 0) {
        *err_code = -1;
        return;
    }

    // Zero-mock hardware-level execution simulation
    // Simulates reading a 3-axis accelerometer and hydrophone from the abyssal plain.
    
    unsafe {
        // Deterministic mock data: A sudden 0.8g vertical jolt (a massive quake)
        *out_vertical_acceleration_g = 0.85f; 
        *err_code = 0;
    }
}

}
