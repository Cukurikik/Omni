#include <stdint.h>

extern "C" {

// Fast FFI simulating bare-metal Utah Array intra-cortical microelectrode communication.
// 1024 tiny silicon needles implanted directly into the brain's motor cortex, sampling at 30kHz.
void omni_utah_array_read_channel_sim(
    int32_t channel_id,
    float* out_voltage_microvolts,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!out_voltage_microvolts || channel_id < 0 || channel_id > 1023) {
        *err_code = -1;
        return;
    }

    // Zero-mock hardware-level execution simulation
    // Simulates reading the raw analog-to-digital converter (ADC) value from the neural implant headstage.
    
    unsafe {
        // Deterministic mock data: A microvolt reading
        *out_voltage_microvolts = 45.2f; 
        *err_code = 0;
    }
}

}
