#include <cstdint>
extern "C" {
    uint32_t omni_sys_ai_renamer_levenshtein(const char* s1, int len1, const char* s2, int len2) {
        if (!s1 || !s2) return 0;
        if (len1 == 0) return len2;
        if (len2 == 0) return len1;
        uint32_t prev[256], curr[256];
        for (int j = 0; j <= len2 && j < 256; ++j) prev[j] = j;
        for (int i = 1; i <= len1; ++i) {
            curr[0] = i;
            for (int j = 1; j <= len2 && j < 256; ++j) {
                int cost = (s1[i-1] == s2[j-1]) ? 0 : 1;
                uint32_t a = prev[j] + 1, b = curr[j-1] + 1, c = prev[j-1] + cost;
                curr[j] = (a < b) ? (a < c ? a : c) : (b < c ? b : c);
            }
            for (int j = 0; j <= len2 && j < 256; ++j) prev[j] = curr[j];
        }
        return prev[len2 < 256 ? len2 : 255];
    }
}
