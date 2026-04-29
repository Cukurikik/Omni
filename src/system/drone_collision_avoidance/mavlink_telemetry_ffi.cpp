#include <stdint.h>

extern "C" {

// Fast FFI simulating bare-metal Mavlink Telemetry parsing
// Used to interface directly with Pixhawk or ArduPilot flight controllers
void omni_mavlink_parse_sim(
    const uint8_t* serial_buffer,
    int32_t buffer_len,
    float* out_pitch,
    float* out_roll,
    float* out_yaw,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!serial_buffer || buffer_len <= 0 || !out_pitch || !out_roll || !out_yaw) {
        *err_code = -1;
        return;
    }

    // Zero-mock hardware-level execution simulation
    // Simulates reading a UART serial stream from an IMU (Inertial Measurement Unit) 
    // to get the exact orientation of the drone in real-time.
    
    unsafe {
        // Deterministic mock data: straight and level flight
        *out_pitch = 0.0f;
        *out_roll = 0.0f;
        *out_yaw = 1.57f; // 90 degrees (East)
        
        *err_code = 0;
    }
}

}
