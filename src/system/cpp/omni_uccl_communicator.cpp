#include "omni_uccl_communicator.hpp"
#include <stdexcept>
#include <iostream>
#include <cuda.h>

namespace omni {
namespace system {
namespace uccl {

UcclCommunicator::UcclCommunicator(int rank, int world_size, int gpu_id)
    : rank_(rank), world_size_(world_size), gpu_id_(gpu_id), initialized_(false) {
}

UcclCommunicator::~UcclCommunicator() {
    if (initialized_) {
        for (int i = 0; i < world_size_; ++i) {
            if (i != rank_ && peer_buffers_[i] != nullptr) {
                cudaIpcCloseMemHandle(peer_buffers_[i]);
            }
        }
        cudaEventDestroy(sync_event_);
    }
}

void UcclCommunicator::initialize() {
    cudaSetDevice(gpu_id_);
    cudaEventCreateWithFlags(&sync_event_, cudaEventDisableTiming);
    peer_buffers_.resize(world_size_, nullptr);
    setup_peer_access();
    initialized_ = true;
}

void UcclCommunicator::setup_peer_access() {
    for (int i = 0; i < world_size_; ++i) {
        if (i == rank_) continue;
        int can_access = 0;
        cudaDeviceCanAccessPeer(&can_access, gpu_id_, i);
        if (can_access) {
            cudaDeviceEnablePeerAccess(i, 0);
        }
    }
}

void UcclCommunicator::all_to_all_v(
    const void* send_buffer,
    const size_t* send_counts,
    const size_t* send_displacements,
    void* recv_buffer,
    const size_t* recv_counts,
    const size_t* recv_displacements,
    cudaStream_t stream
) {
    if (!initialized_) {
        throw std::runtime_error("UcclCommunicator not initialized");
    }

    const uint8_t* send_ptr = static_cast<const uint8_t*>(send_buffer);
    uint8_t* recv_ptr = static_cast<uint8_t*>(recv_buffer);

    // Direct GPU-to-GPU memory copy using peer-to-peer DMA engines
    for (int i = 0; i < world_size_; ++i) {
        size_t s_count = send_counts[i];
        size_t s_disp = send_displacements[i];
        size_t r_count = recv_counts[i];
        size_t r_disp = recv_displacements[i];

        if (s_count > 0 && i != rank_) {
            // In a real multi-node cluster, this would invoke RDMA via IBV verbs.
            // For single-node multi-GPU, cudaMemcpyAsync handles P2P DMA natively.
            cudaMemcpyAsync(
                peer_buffers_[i], 
                send_ptr + s_disp, 
                s_count, 
                cudaMemcpyDeviceToDevice, 
                stream
            );
        } else if (s_count > 0 && i == rank_) {
            cudaMemcpyAsync(
                recv_ptr + r_disp,
                send_ptr + s_disp,
                s_count,
                cudaMemcpyDeviceToDevice,
                stream
            );
        }
    }
    
    cudaEventRecord(sync_event_, stream);
    cudaStreamWaitEvent(stream, sync_event_, 0);
}

} // namespace uccl
} // namespace system
} // namespace omni
