// moe_mnemocuda_page_cache.cpp — System Layer: MnemoCUDA Page Cache
// C++ LRU page cache for managing 235B+ MoE weights resident in limited VRAM.

#include <unordered_map>
#include <list>
#include <cstdint>
#include <mutex>

namespace omni {
namespace system {
namespace mnemocuda {

struct ExpertPage {
    uint32_t expert_id;
    uint64_t vram_offset;
    bool is_dirty;
};

class VramPageCache {
private:
    size_t capacity;
    std::list<ExpertPage> lru_list;
    std::unordered_map<uint32_t, decltype(lru_list.begin())> page_map;
    std::mutex cache_mutex;

public:
    VramPageCache(size_t max_pages) : capacity(max_pages) {}

    bool request_expert(uint32_t expert_id, uint64_t& out_vram_offset) {
        std::lock_guard<std::mutex> lock(cache_mutex);
        
        auto it = page_map.find(expert_id);
        if (it != page_map.end()) {
            // Cache hit, move to front
            lru_list.splice(lru_list.begin(), lru_list, it->second);
            out_vram_offset = it->second->vram_offset;
            return true;
        }
        return false;
    }

    uint32_t load_expert(uint32_t expert_id, uint64_t vram_offset) {
        std::lock_guard<std::mutex> lock(cache_mutex);
        
        uint32_t evicted_expert = 0;
        if (lru_list.size() >= capacity) {
            // Evict LRU
            evicted_expert = lru_list.back().expert_id;
            page_map.erase(evicted_expert);
            lru_list.pop_back();
        }

        lru_list.push_front({expert_id, vram_offset, false});
        page_map[expert_id] = lru_list.begin();

        return evicted_expert; // Returns 0 if no eviction, or ID of evicted expert
    }
};

} // namespace mnemocuda
} // namespace system
} // namespace omni
