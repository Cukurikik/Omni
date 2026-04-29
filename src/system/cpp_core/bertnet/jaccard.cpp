#include <cstdint>
#include <algorithm>
#include <vector>

extern "C" {
    // OMNI System Layer - Computes Jaccard on sorted integer arrays
    double compute_jaccard_sim(const int32_t* a, int32_t len_a, const int32_t* b, int32_t len_b) {
        if (!a || !b || (len_a == 0 && len_b == 0)) return 1.0;
        
        int32_t i = 0, j = 0;
        int32_t intersection_size = 0;
        
        while (i < len_a && j < len_b) {
            if (a[i] < b[j]) {
                i++;
            } else if (a[i] > b[j]) {
                j++;
            } else {
                intersection_size++;
                i++;
                j++;
            }
        }
        
        int32_t union_size = len_a + len_b - intersection_size;
        return union_size == 0 ? 0.0 : (double)intersection_size / union_size;
    }
}
