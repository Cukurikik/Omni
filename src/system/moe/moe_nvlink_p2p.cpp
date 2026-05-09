// moe_nvlink_p2p.cpp — System / Interconnect
// Layer: System / Memory — CUDA IPC Peer-to-Peer Transfer
//
// In multi-GPU nodes (e.g. 8x H100), passing tokens between experts on different
// GPUs via the CPU causes a massive PCIe bottleneck. This module implements
// bare-metal CUDA IPC (Inter-Process Communication) to allow GPU 0 to write
// tokens directly into the VRAM of GPU 1 over NVLink.

#include <iostream>
#include <cuda_runtime.h>
#include <vector>

namespace omni {
namespace moe {
namespace ipc {

void checkCuda(cudaError_t err, const char* msg) {
    if (err != cudaSuccess) {
        std::cerr << "[CUDA P2P] " << msg << " failed: " << cudaGetErrorString(err) << std::endl;
        exit(1);
    }
}

class GpuP2PTransfer {
public:
    GpuP2PTransfer() {
        std::cout << "[CUDA P2P] Initialized NVLink/PCIe Peer-to-Peer transfer engine." << std::endl;
    }

    /**
     * @brief Enables direct VRAM-to-VRAM access between two GPUs.
     * Must be called during system initialization.
     */
    void enable_p2p_access(int src_gpu_id, int dest_gpu_id) {
        int can_access = 0;
        checkCuda(cudaDeviceCanAccessPeer(&can_access, src_gpu_id, dest_gpu_id), "Check Peer Access");
        
        if (can_access) {
            checkCuda(cudaSetDevice(src_gpu_id), "Set Src Device");
            // Ignore error if already enabled
            cudaError_t err = cudaDeviceEnablePeerAccess(dest_gpu_id, 0);
            if (err != cudaSuccess && err != cudaErrorPeerAccessAlreadyEnabled) {
                checkCuda(err, "Enable Peer Access");
            }
            std::cout << "[CUDA P2P] Enabled direct P2P access: GPU " << src_gpu_id << " -> GPU " << dest_gpu_id << std::endl;
        } else {
            std::cerr << "[CUDA P2P] WARNING: P2P access not supported between GPU " << src_gpu_id << " and " << dest_gpu_id << std::endl;
        }
    }

    /**
     * @brief Executes the direct VRAM copy bypassing host memory.
     */
    void transfer_tokens_p2p(void* dst_ptr, const void* src_ptr, size_t size_bytes, cudaStream_t stream) {
        // Since P2P is enabled, cudaMemcpyAsync automatically detects the pointers are on different GPUs
        // and routes the transfer over NVLink or PCIe switch directly.
        checkCuda(cudaMemcpyAsync(dst_ptr, src_ptr, size_bytes, cudaMemcpyDeviceToDevice, stream), "P2P Copy");
    }
};

} // namespace ipc
} // namespace moe
} // namespace omni
