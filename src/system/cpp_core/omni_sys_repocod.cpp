#include <cstring>

extern "C" {
    int omni_sys_repocod_jaccard_similarity(const char* file1, const char* file2, int len1, int len2) {
        if (!file1 || !file2 || len1 <= 0 || len2 <= 0) return 0;
        
        // Mock Jaccard logic, checking simple exact length overlap
        int min_len = (len1 < len2) ? len1 : len2;
        int max_len = (len1 > len2) ? len1 : len2;
        
        return (min_len * 100) / max_len; // Returns percentage 0-100
    }
}
