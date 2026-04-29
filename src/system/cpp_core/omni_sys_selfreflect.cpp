#include <cstdint>

extern "C" {
    struct MemorySnapshot {
        int64_t id;
        int64_t state_hash;
    };

    int omni_sys_selfreflect_rollback(MemorySnapshot* snapshots, int count, int64_t target_hash) {
        if (count <= 0) return -1;
        
        for (int i = count - 1; i >= 0; --i) {
            if (snapshots[i].state_hash == target_hash) {
                return i; // Index to rollback to
            }
        }
        return -1; // Not found
    }
}
