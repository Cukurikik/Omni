#include <cstdint>
extern "C" {
    uint64_t omni_sys_ai_blueprints_dag_hash(const int* edges, int num_edges) {
        if (!edges || num_edges <= 0) return 0;
        uint64_t h = 14695981039346656037ULL;
        for (int i = 0; i < num_edges * 2; ++i) {
            h ^= (uint64_t)edges[i];
            h *= 1099511628211ULL;
        }
        return h;
    }
    int omni_sys_ai_blueprints_critical_path(const int* durations, int n) {
        if (!durations || n <= 0) return 0;
        int max_d = 0;
        for (int i = 0; i < n; ++i) if (durations[i] > max_d) max_d = durations[i];
        return max_d;
    }
}
