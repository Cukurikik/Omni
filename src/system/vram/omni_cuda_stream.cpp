// omni_cuda_stream.cpp — CUDA Stream Manager
// Layer: System / CUDA
//
// Safe C++ wrapper around CUDA Streams and Events to enable highly asynchronous
// kernel launches, memory transfers, and synchronization across the GPU.

#include <cuda_runtime.h>
#include <stdexcept>
#include <string>
#include <iostream>

#define CHECK_CUDA(call) \
do { \
    cudaError_t err = call; \
    if (err != cudaSuccess) { \
        throw std::runtime_error("CUDA Error: " + std::string(cudaGetErrorString(err))); \
    } \
} while (0)

class OmniCudaStream {
private:
    cudaStream_t stream;
    bool is_destroyed;

public:
    OmniCudaStream(bool non_blocking = true) : is_destroyed(false) {
        unsigned int flags = non_blocking ? cudaStreamNonBlocking : cudaStreamDefault;
        CHECK_CUDA(cudaStreamCreateWithFlags(&stream, flags));
    }

    ~OmniCudaStream() {
        if (!is_destroyed) {
            cudaStreamDestroy(stream);
        }
    }

    cudaStream_t get() const {
        return stream;
    }

    void synchronize() const {
        CHECK_CUDA(cudaStreamSynchronize(stream));
    }

    // Prevents double deletion if moved
    OmniCudaStream(OmniCudaStream&& other) noexcept : stream(other.stream), is_destroyed(other.is_destroyed) {
        other.is_destroyed = true;
    }
};

class OmniCudaEvent {
private:
    cudaEvent_t event;
    bool is_destroyed;

public:
    OmniCudaEvent(bool disable_timing = false) : is_destroyed(false) {
        unsigned int flags = disable_timing ? cudaEventDisableTiming : cudaEventDefault;
        CHECK_CUDA(cudaEventCreateWithFlags(&event, flags));
    }

    ~OmniCudaEvent() {
        if (!is_destroyed) {
            cudaEventDestroy(event);
        }
    }

    void record(const OmniCudaStream& stream) {
        CHECK_CUDA(cudaEventRecord(event, stream.get()));
    }

    void synchronize() const {
        CHECK_CUDA(cudaEventSynchronize(event));
    }

    float elapsed_time(const OmniCudaEvent& end_event) const {
        float ms = 0.0f;
        CHECK_CUDA(cudaEventElapsedTime(&ms, event, end_event.event));
        return ms;
    }
};
