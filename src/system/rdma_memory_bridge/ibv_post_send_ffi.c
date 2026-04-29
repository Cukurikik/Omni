#include <stdint.h>

extern "C" {

// Fast FFI simulating bare-metal Infiniband Verbs API (ibv_post_send)
// Pushes a work request directly to the Mellanox/NVIDIA ConnectX NIC hardware queue
void omni_ibv_post_send_sim(
    uint64_t memory_address,
    int32_t length_bytes,
    int32_t target_queue_pair_id,
    int32_t* err_code
) {
    if (!err_code) return;

    if (length_bytes <= 0 || target_queue_pair_id < 0) {
        *err_code = -1;
        return;
    }

    // Zero-mock hardware-level execution simulation
    // In production, this rings the "doorbell" on the NIC via PCIe memory-mapped I/O (MMIO),
    // instructing the NIC to DMA the memory and send it over the fiber optic cable without involving the OS Kernel.
    
    // Deterministic mock success
    *err_code = 0;
}

}
