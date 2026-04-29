#include <cstdint>
#include <algorithm>

extern "C" {
    // OMNI System Layer - Fast path length calculator for flat arrays representing tree edges
    int32_t compute_flat_dag_depth(const int32_t* parents, int32_t len) {
        if (!parents || len <= 0) return 0;
        int32_t max_depth = 0;
        
        for (int32_t i = 0; i < len; ++i) {
            int32_t depth = 1;
            int32_t curr = i;
            while (parents[curr] != -1 && depth < len) {
                curr = parents[curr];
                depth++;
            }
            if (depth > max_depth) {
                max_depth = depth;
            }
        }
        return max_depth;
    }
}
