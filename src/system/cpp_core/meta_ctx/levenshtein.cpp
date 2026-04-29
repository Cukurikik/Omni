#include <cstdint>
#include <algorithm>
#include <vector>

extern "C" {
    // OMNI System Layer - Fast Levenshtein distance array kernel
    int32_t compute_levenshtein_distance(const char* s1, int32_t len1, const char* s2, int32_t len2) {
        if (len1 == 0) return len2;
        if (len2 == 0) return len1;
        
        std::vector<int32_t> v0(len2 + 1);
        std::vector<int32_t> v1(len2 + 1);
        
        for (int32_t i = 0; i <= len2; i++) v0[i] = i;
        
        for (int32_t i = 0; i < len1; i++) {
            v1[0] = i + 1;
            for (int32_t j = 0; j < len2; j++) {
                int32_t cost = (s1[i] == s2[j]) ? 0 : 1;
                v1[j + 1] = std::min({ v1[j] + 1, v0[j + 1] + 1, v0[j] + cost });
            }
            for (int32_t j = 0; j <= len2; j++) v0[j] = v1[j];
        }
        return v0[len2];
    }
}
