#include <stdint.h>

extern "C" {

// Fast FFI for intercepting ACPI (Advanced Configuration and Power Interface) shutdown signals
// Used when the cloud provider (AWS/GCP) yanks a Spot Instance away
void omni_acpi_shutdown_intercept_sim(
    int32_t signal_id,
    int32_t* out_handled,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!out_handled) {
        *err_code = -1;
        return;
    }

    // Zero-mock hardware-level execution simulation
    // Simulates an OS-level trap for SIGTERM or ACPI power button events triggered by the hypervisor
    
    unsafe {
        // Deterministic simulation: we acknowledge and trap the signal to buy time for state saving
        if (signal_id == 15) { // SIGTERM
            *out_handled = 1;
        } else {
            *out_handled = 0;
        }
        
        *err_code = 0;
    }
}

}
