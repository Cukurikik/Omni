#include <cstdint>
#include <cstdlib>
#include <mutex>
#include <unordered_map>

namespace OmniH2O {

class MemoryManager {
private:
    std::mutex mtx;
    std::unordered_map<void*, size_t> allocations;
    size_t total_allocated = 0;

public:
    void* allocate(size_t size) {
        void* ptr = std::malloc(size);
        if (ptr) {
            std::lock_guard<std::mutex> lock(mtx);
            allocations[ptr] = size;
            total_allocated += size;
        }
        return ptr;
    }

    void deallocate(void* ptr) {
        if (!ptr) return;
        std::lock_guard<std::mutex> lock(mtx);
        auto it = allocations.find(ptr);
        if (it != allocations.end()) {
            total_allocated -= it->second;
            allocations.erase(it);
            std::free(ptr);
        }
    }
    
    size_t get_total_allocated() { return total_allocated; }
};

}
