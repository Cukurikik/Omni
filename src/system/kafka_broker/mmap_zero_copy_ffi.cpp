#include <stdint.h>

extern "C" {

// Fast FFI simulating Linux mmap() for zero-copy file to network transfer (sendfile mechanism)
void omni_mmap_zero_copy_sim(
    int32_t file_descriptor,
    int32_t socket_descriptor,
    int64_t offset,
    int64_t bytes_to_send,
    int64_t* out_bytes_sent,
    int32_t* err_code
) {
    if (!err_code) return;

    if (file_descriptor < 0 || socket_descriptor < 0 || !out_bytes_sent) {
        *err_code = -1;
        return;
    }

    if (bytes_to_send <= 0) {
        *err_code = -2;
        return;
    }

    // Zero-mock deterministic simulation
    // In production, this directly invokes the OS sendfile() system call
    // bypassing userspace buffers completely.
    
    *out_bytes_sent = bytes_to_send; // Simulated successful zero-copy transfer
    *err_code = 0;
}

}
