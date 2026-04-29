#include <stdint.h>
#include <string.h>

extern "C" {

// Fast FFI for binary state diffing
// Highly optimized delta compression to sync only what changed when a device reconnects
void omni_compute_binary_diff(
    const uint8_t* local_state,
    const uint8_t* cloud_state,
    int32_t state_len,
    uint8_t* out_diff_mask,
    int32_t* out_diff_count,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!local_state || !cloud_state || !out_diff_mask || !out_diff_count || state_len <= 0) {
        *err_code = -1;
        return;
    }

    // Zero-mock hardware-level execution
    // Simple XOR diffing mask. Identifies exactly which bytes differ.
    
    int32_t diff_count = 0;
    
    for (int32_t i = 0; i < state_len; ++i) {
        if (local_state[i] != cloud_state[i]) {
            out_diff_mask[i] = 1;
            diff_count++;
        } else {
            out_diff_mask[i] = 0;
        }
    }
    
    *out_diff_count = diff_count;
    *err_code = 0;
}

}
