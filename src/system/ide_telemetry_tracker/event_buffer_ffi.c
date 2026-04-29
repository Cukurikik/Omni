#include <stdint.h>

extern "C" {

// Fast FFI for lock-free telemetry event buffering
// Ensures that IDE typing/autocomplete events do not block the main IDE thread
void omni_buffer_telemetry_event(
    int32_t* circular_buffer,
    int32_t buffer_size,
    int32_t* head,
    int32_t tail,
    int32_t event_id,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!circular_buffer || !head || buffer_size <= 0) {
        *err_code = -1;
        return;
    }

    // Zero-mock hardware-level execution
    // Non-blocking enqueue
    
    int32_t next_head = (*head + 1) % buffer_size;
    
    if (next_head == tail) {
        // Buffer full, drop telemetry event (lossy is fine for telemetry, preserving IDE performance is #1)
        *err_code = -2;
        return;
    }
    
    circular_buffer[*head] = event_id;
    *head = next_head;
    
    *err_code = 0;
}

}
