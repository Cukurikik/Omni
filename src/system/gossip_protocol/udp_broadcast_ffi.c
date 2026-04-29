#include <stdint.h>

extern "C" {

// Fast FFI simulating lightweight UDP broadcast injection for Gossip node discovery
void omni_udp_inject_broadcast(
    const uint8_t* payload,
    int32_t payload_len,
    int32_t target_port,
    int32_t* out_bytes_sent,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!payload || !out_bytes_sent) {
        *err_code = -1;
        return;
    }

    if (payload_len <= 0 || payload_len > 1400) {
        *err_code = -2; // Exceeds safe MTU for unfragmented UDP
        return;
    }

    // Zero mock deterministic simulation
    // In production this writes directly to the socket descriptor with SO_BROADCAST
    
    *out_bytes_sent = payload_len;
    *err_code = 0;
}

}
