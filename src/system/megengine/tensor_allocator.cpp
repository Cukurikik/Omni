#include <iostream>
#include <vector>
#include <stdexcept>
#include <memory>
#include <cuda_runtime.h>

// OMNI C++ System Layer: MegEngine Tensor Allocator
// Zero-copy, page-locked memory allocator for high-performance deep learning.

namespace omni::megengine {

    template<typename T>
    struct Result {
        T value;
        std::string error;
        bool is_ok;

        static Result<T> Ok(T val) { return {val, "", true}; }
        static Result<T> Err(std::string err) { return {T(), err, false}; }
    };

    class PinnedTensorAllocator {
    public:
        PinnedTensorAllocator() = default;

        Result<void*> allocate(size_t num_bytes) {
            void* ptr = nullptr;
            cudaError_t err = cudaMallocHost(&ptr, num_bytes);
            if (err != cudaSuccess) {
                return Result<void*>::Err(std::string("CUDA MallocHost failed: ") + cudaGetErrorString(err));
            }
            return Result<void*>::Ok(ptr);
        }

        Result<bool> deallocate(void* ptr) {
            if (ptr == nullptr) {
                return Result<bool>::Err("Attempted to free null pointer");
            }
            cudaError_t err = cudaFreeHost(ptr);
            if (err != cudaSuccess) {
                return Result<bool>::Err(std::string("CUDA FreeHost failed: ") + cudaGetErrorString(err));
            }
            return Result<bool>::Ok(true);
        }
    };

    extern "C" {
        void* omni_megengine_alloc(size_t bytes) {
            PinnedTensorAllocator allocator;
            auto res = allocator.allocate(bytes);
            if (!res.is_ok) {
                std::cerr << "CRITICAL: " << res.error << std::endl;
                return nullptr;
            }
            return res.value;
        }

        void omni_megengine_free(void* ptr) {
            PinnedTensorAllocator allocator;
            auto res = allocator.deallocate(ptr);
            if (!res.is_ok) {
                std::cerr << "CRITICAL: " << res.error << std::endl;
            }
        }
    }
}
