#include <cuda_runtime.h>
#include <stdexcept>
#include <string>

// Omni CUDA C++ Bridge
// FFI-safe wrapper for high-performance compute kernels

extern "C" cudaError_t launch_snn_kernel(float* d_potentials, const float* d_spikes, float threshold, float decay, int num_neurons);

struct CudaResult {
    bool success;
    std::string error_msg;
};

class OmniCudaBridge {
public:
    static CudaResult execute_snn(float* potentials, const float* spikes, int num_neurons) {
        if (!potentials || !spikes || num_neurons <= 0) {
            return {false, "Invalid inputs to CUDA bridge"};
        }

        cudaError_t status = launch_snn_kernel(potentials, spikes, 1.0f, 0.9f, num_neurons);
        
        if (status != cudaSuccess) {
            return {false, cudaGetErrorString(status)};
        }

        return {true, ""};
    }
};
