#include <stdint.h>

extern "C" {

// Fast FFI for reading I2C thermal sensors directly off the ASIC PCB
// Bypasses high-level OS polling to get real-time silicon die temperatures
void omni_read_i2c_temp_sim(
    int32_t sensor_bus_id,
    double* out_temp_celsius,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!out_temp_celsius || sensor_bus_id < 0) {
        *err_code = -1;
        return;
    }

    // Zero-mock hardware-level execution simulation
    // Simulates reading a digital temperature sensor (e.g. TMP102) over an I2C bus
    unsafe {
        // Deterministic mock data: Simulate a hot AI chip under load (e.g., 82.5 C)
        *out_temp_celsius = 82.5;
        *err_code = 0;
    }
}

}
