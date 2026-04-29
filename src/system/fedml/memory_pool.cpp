#include <vector>
#include <mutex>
#include <stdexcept>

// OMNI FEDML: Fast Tensor Memory Pool (C++)
// Pre-allocated contiguous memory management to avoid fragmentation during high-frequency federated gradient updates.
// Source: FedML-AI/FedML

namespace omni::fedml {

enum class PoolError {
    SUCCESS,
    OUT_OF_MEMORY,
    INVALID_SIZE,
    DOUBLE_FREE
};

template<typename T, typename E>
struct Result {
    T value;
    E error;
    bool is_ok() const { return error == PoolError::SUCCESS; }
};

class TensorMemoryPool {
private:
    std::vector<uint8_t> pool;
    std::vector<bool> allocation_map; // True if block is free
    size_t block_size;
    size_t num_blocks;
    std::mutex mtx;

public:
    TensorMemoryPool(size_t block_size_bytes, size_t total_blocks) 
        : block_size(block_size_bytes), num_blocks(total_blocks) {
        
        pool.resize(block_size * num_blocks);
        allocation_map.resize(num_blocks, true);
    }

    Result<void*, PoolError> allocate() {
        std::lock_guard<std::mutex> lock(mtx);
        
        for (size_t i = 0; i < num_blocks; ++i) {
            if (allocation_map[i]) {
                allocation_map[i] = false; // Mark as used
                void* ptr = static_cast<void*>(&pool[i * block_size]);
                return {ptr, PoolError::SUCCESS};
            }
        }
        
        return {nullptr, PoolError::OUT_OF_MEMORY};
    }

    PoolError deallocate(void* ptr) {
        if (!ptr) return PoolError::INVALID_SIZE;
        
        std::lock_guard<std::mutex> lock(mtx);
        
        uint8_t* byte_ptr = static_cast<uint8_t*>(ptr);
        uint8_t* pool_start = pool.data();
        
        // Calculate block index based on pointer math
        size_t offset = byte_ptr - pool_start;
        if (offset % block_size != 0 || offset >= pool.size()) {
            return PoolError::INVALID_SIZE;
        }
        
        size_t block_idx = offset / block_size;
        
        if (allocation_map[block_idx]) {
            return PoolError::DOUBLE_FREE;
        }
        
        allocation_map[block_idx] = true; // Free it
        return PoolError::SUCCESS;
    }
};

} // namespace omni::fedml
