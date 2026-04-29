#include <cstring>
#include <algorithm>

extern "C" {
    int omni_sys_coedit_levenshtein(const char* s1, const char* s2) {
        if (!s1 || !s2) return -1;
        
        int len1 = std::strlen(s1);
        int len2 = std::strlen(s2);
        
        int matrix[100][100]; // Fixed bounds for deterministic kernel
        if (len1 >= 100 || len2 >= 100) return -1;
        
        for (int i = 0; i <= len1; i++) matrix[i][0] = i;
        for (int j = 0; j <= len2; j++) matrix[0][j] = j;
        
        for (int i = 1; i <= len1; i++) {
            for (int j = 1; j <= len2; j++) {
                int cost = (s1[i-1] == s2[j-1]) ? 0 : 1;
                matrix[i][j] = std::min({
                    matrix[i-1][j] + 1,
                    matrix[i][j-1] + 1,
                    matrix[i-1][j-1] + cost
                });
            }
        }
        return matrix[len1][len2];
    }
}
