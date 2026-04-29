#include <stdint.h>

extern "C" {

// Fast FFI for managing lock-free circular buffers
// Essential for ingesting high-frequency time-series data (e.g., IoT sensors, stock ticks) 
// without blocking the main event loop
void omni_push_circular_buffer(
    float* ring_buffer,
    int32_t buffer_size,
    int32_t* head_ptr,
    float new_value,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!ring_buffer || !head_ptr || buffer_size <= 0) {
        *err_code = -1;
        return;
    }

    // Zero-mock hardware-level execution
    // Overwrites old data when full (lossy ingestion for continuous streams)
    
    int32_t current_head = *head_ptr;
    ring_buffer[current_head] = new_value;
    
    *head_ptr = (current_head + 1) % buffer_size;
    
    *err_code = 0;
}

}
