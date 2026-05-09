#ifndef OMNI_UCCL_COMMUNICATOR_HPP
#define OMNI_UCCL_COMMUNICATOR_HPP

#include <vector>
#include <cstdint>
#include <memory>
#include <cuda_runtime.h>

namespace omni {
namespace system {
namespace uccl {

class UcclCommunicator {
public:
    UcclCommunicator(int rank, int world_size, int gpu_id);
    ~UcclCommunicator();

    void initialize();
    
    // Synchronous all-to-all scatter-gather for MoE expert routing
    void all_to_all_v(
        const void* send_buffer,
        const size_t* send_counts,
        const size_t* send_displacements,
        void* recv_buffer,
        const size_t* recv_counts,
        const size_t* recv_displacements,
        cudaStream_t stream
    );

    int get_rank() const { return rank_; }
    int get_world_size() const { return world_size_; }

private:
    int rank_;
    int world_size_;
    int gpu_id_;
    bool initialized_;
    
    // Ring buffer and peer management
    std::vector<void*> peer_buffers_;
    cudaEvent_t sync_event_;

    void setup_peer_access();
    void allocate_shared_memory();
};

} // namespace uccl
} // namespace system
} // namespace omni

#endif // OMNI_UCCL_COMMUNICATOR_HPP
