// OMNI System Layer: quant_agent_memory.cpp
// QuantAgent Memory Manager - Strict 8GB limits for agent trajectories.
// Hardware-aware arena allocator avoiding dynamic memory fragmentation.

#include <cstdint>
#include <cstddef>
#include <new>

// Strict Memory Limits
constexpr size_t MAX_TRAJECTORY_MEMORY = 8ULL * 1024 * 1024 * 1024; // 8GB
constexpr size_t MAX_TRAJECTORIES = 10000;

enum class OmniErrorCode {
    SUCCESS = 0,
    OUT_OF_MEMORY = 1,
    INDEX_OUT_OF_BOUNDS = 2
};

template <typename T>
struct OmniResult {
    T value;
    OmniErrorCode error;
};

// Monolithic Arena
class QuantMemoryArena {
private:
    uint8_t* base_ptr;
    size_t offset;

public:
    QuantMemoryArena() : offset(0) {
        // Pre-allocate the entire block bounded to MAX_TRAJECTORY_MEMORY
        base_ptr = new (std::nothrow) uint8_t[MAX_TRAJECTORY_MEMORY];
        if (!base_ptr) {
            // Unrecoverable at constructor, but handled in init in OMNI
        }
    }

    ~QuantMemoryArena() {
        delete[] base_ptr;
    }

    bool is_valid() const {
        return base_ptr != nullptr;
    }

    OmniResult<void*> allocate(size_t size) {
        if (offset + size > MAX_TRAJECTORY_MEMORY) {
            return {nullptr, OmniErrorCode::OUT_OF_MEMORY};
        }
        void* ptr = base_ptr + offset;
        offset += size;
        return {ptr, OmniErrorCode::SUCCESS};
    }

    void reset() {
        offset = 0; // O(1) clear of all agent trajectories
    }
};

// Global Agent Instance Memory
static QuantMemoryArena GlobalQuantArena;

// C-FFI Export for OMNI Runtime
extern "C" {

    int omni_quant_init() {
        return GlobalQuantArena.is_valid() ? 0 : 1;
    }

    void* omni_quant_alloc_trajectory(size_t size) {
        auto res = GlobalQuantArena.allocate(size);
        if (res.error != OmniErrorCode::SUCCESS) {
            return nullptr;
        }
        return res.value;
    }

    void omni_quant_reset() {
        GlobalQuantArena.reset();
    }
}
