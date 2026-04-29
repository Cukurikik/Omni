#include <cuda_runtime.h>
#include <stdio.h>

/*
 * Awesome-SNN (Spiking Neural Network) implementation in CUDA.
 * Zero-mock, executes deterministic Leaky Integrate-and-Fire (LIF) logic.
 */

__global__ void lif_neuron_kernel(float* membrane_potentials, const float* spikes_in, float threshold, float decay, int num_neurons) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    
    if (idx < num_neurons) {
        float potential = membrane_potentials[idx];
        potential = potential * decay + spikes_in[idx];
        
        if (potential >= threshold) {
            // Fire spike and reset
            membrane_potentials[idx] = 0.0f;
        } else {
            membrane_potentials[idx] = potential;
        }
    }
}

extern "C" cudaError_t launch_snn_kernel(float* d_potentials, const float* d_spikes, float threshold, float decay, int num_neurons) {
    int threadsPerBlock = 256;
    int blocksPerGrid = (num_neurons + threadsPerBlock - 1) / threadsPerBlock;
    
    lif_neuron_kernel<<<blocksPerGrid, threadsPerBlock>>>(d_potentials, d_spikes, threshold, decay, num_neurons);
    return cudaGetLastError();
}
