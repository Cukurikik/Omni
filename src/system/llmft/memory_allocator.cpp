#include <cstdlib>
#include <string>

namespace omni {
namespace llmft {

template<typename T>
struct OmniResult {
    T* value;
    std::string error;
    bool is_ok;
};

class MemoryAllocator {
public:
    OmniResult<void> allocate_tensor_memory(size_t bytes) {
        if (bytes == 0) {
            return {nullptr, "Cannot allocate 0 bytes", false};
        }
        
        // C++ high-speed allocator for LLM-FT weights
        void* ptr = std::malloc(bytes);
        if (!ptr) {
            return {nullptr, "OOM", false};
        }
        
        return {ptr, "", true};
    }
};

}
}
