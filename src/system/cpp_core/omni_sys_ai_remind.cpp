#include <cstdint>
extern "C" {
    int omni_sys_ai_remind_lru_evict(int* cache_ages, int capacity, int new_item_age) {
        if (!cache_ages || capacity <= 0) return -1;
        int oldest_idx = 0;
        for (int i = 1; i < capacity; ++i) {
            if (cache_ages[i] > cache_ages[oldest_idx]) oldest_idx = i;
        }
        cache_ages[oldest_idx] = new_item_age;
        return oldest_idx;
    }
}
