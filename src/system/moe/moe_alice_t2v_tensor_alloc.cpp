// moe_alice_t2v_tensor_alloc.cpp — System
// Layer: System — Memory Allocator for Video Generation MoE
// Inspired by: Eric-Alice-T2V-ComfyUI-Wrapper

#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <mutex>

namespace omni {
namespace system {

class VideoTensorAllocator {
private:
    uint8_t* memory_pool;
    size_t total_capacity;
    size_t current_offset;
    std::mutex alloc_mutex;

public:
    VideoTensorAllocator(size_t capacity_gb) {
        total_capacity = capacity_gb * 1024 * 1024 * 1024;
        memory_pool = static_cast<uint8_t*>(std::malloc(total_capacity));
        current_offset = 0;
        if (!memory_pool) {
            std::cerr << "Failed to allocate " << capacity_gb << " GB for Video Tensors.\n";
            std::exit(EXIT_FAILURE);
        }
    }

    ~VideoTensorAllocator() {
        std::free(memory_pool);
    }

    // Zero-copy slice allocation for ComfyUI spatial/temporal frames
    uint8_t* allocate_frame_buffer(size_t width, size_t height, size_t channels, size_t frames) {
        std::lock_guard<std::mutex> lock(alloc_mutex);
        size_t required = width * height * channels * frames * sizeof(float);
        
        // Align to 256 bytes for AVX/CUDA efficiency
        size_t remainder = required % 256;
        if (remainder != 0) required += (256 - remainder);

        if (current_offset + required > total_capacity) {
            return nullptr; // OOM condition handled by caller
        }

        uint8_t* ptr = memory_pool + current_offset;
        current_offset += required;
        return ptr;
    }
    
    void reset() {
        std::lock_guard<std::mutex> lock(alloc_mutex);
        current_offset = 0;
    }
};

}} // namespace
