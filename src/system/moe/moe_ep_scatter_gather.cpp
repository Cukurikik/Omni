// moe_ep_scatter_gather.cpp — System / GPU
// Layer: Compute / C++ — Expert Parallelism Primitives
//
// Wraps MPI/CUDA IPC for low-latency Scatter and Gather operations.
// Used when distributing tokens to experts residing on different GPUs.

#include <vector>
#include <cstring>
#include <stdexcept>

// Mock definitions for MPI and CUDA
typedef int MPI_Comm;
typedef void* cudaStream_t;
const int MPI_FLOAT = 1;
const int MPI_SUM = 2;

int MPI_Scatterv(const void *sendbuf, const int *sendcounts, const int *displs,
                 int sendtype, void *recvbuf, int recvcount, int recvtype,
                 int root, MPI_Comm comm) { return 0; }

int MPI_Gatherv(const void *sendbuf, int sendcount, int sendtype,
                void *recvbuf, const int *recvcounts, const int *displs,
                int recvtype, int root, MPI_Comm comm) { return 0; }

namespace omni {
namespace moe {

class EPScatterGather {
private:
    MPI_Comm comm_;
    int rank_;
    int world_size_;

public:
    EPScatterGather(MPI_Comm comm, int rank, int world_size)
        : comm_(comm), rank_(rank), world_size_(world_size) {}

    /**
     * Scatter tokens from the coordinator (rank 0) to all expert nodes.
     * @param global_tokens Buffer containing all tokens (valid only on root)
     * @param send_counts Number of tokens going to each node
     * @param displacements Offsets into global_tokens
     * @param local_tokens Buffer to receive tokens for the local expert
     * @param recv_count Number of tokens expected locally
     * @param token_dim Dimensionality of each token
     */
    void scatter_tokens(
        const float* global_tokens,
        const int* send_counts,
        const int* displacements,
        float* local_tokens,
        int recv_count,
        int token_dim
    ) {
        // Adjust counts and displacements by token_dim
        std::vector<int> adj_send_counts(world_size_);
        std::vector<int> adj_displs(world_size_);
        
        if (rank_ == 0) {
            for (int i = 0; i < world_size_; ++i) {
                adj_send_counts[i] = send_counts[i] * token_dim;
                adj_displs[i] = displacements[i] * token_dim;
            }
        }

        MPI_Scatterv(
            global_tokens,
            adj_send_counts.data(),
            adj_displs.data(),
            MPI_FLOAT,
            local_tokens,
            recv_count * token_dim,
            MPI_FLOAT,
            0,
            comm_
        );
    }

    /**
     * Gather computed tokens from all expert nodes back to the coordinator.
     */
    void gather_tokens(
        const float* local_tokens,
        int send_count,
        float* global_tokens,
        const int* recv_counts,
        const int* displacements,
        int token_dim
    ) {
        std::vector<int> adj_recv_counts(world_size_);
        std::vector<int> adj_displs(world_size_);
        
        if (rank_ == 0) {
            for (int i = 0; i < world_size_; ++i) {
                adj_recv_counts[i] = recv_counts[i] * token_dim;
                adj_displs[i] = displacements[i] * token_dim;
            }
        }

        MPI_Gatherv(
            local_tokens,
            send_count * token_dim,
            MPI_FLOAT,
            global_tokens,
            adj_recv_counts.data(),
            adj_displs.data(),
            MPI_FLOAT,
            0,
            comm_
        );
    }
};

} // namespace moe
} // namespace omni
