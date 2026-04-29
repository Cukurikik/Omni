#include <string.h>
#include <stdlib.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    int is_success;
    int value;
    int error_code; // 1 = alloc failure, 2 = null strings
} EditDistanceResult;

EditDistanceResult levenshtein_distance(const char *s1, const char *s2) {
    EditDistanceResult res = {0, 0, 0};
    
    if (s1 == NULL || s2 == NULL) {
        res.error_code = 2;
        return res;
    }
    
    unsigned int s1len = strlen(s1);
    unsigned int s2len = strlen(s2);
    
    // Memory safe allocation with checks
    unsigned int *column = (unsigned int *)malloc((s1len + 1) * sizeof(unsigned int));
    if (column == NULL) {
        res.error_code = 1;
        return res;
    }
    
    for (unsigned int y = 1; y <= s1len; y++) {
        column[y] = y;
    }
    
    for (unsigned int x = 1; x <= s2len; x++) {
        column[0] = x;
        unsigned int lastdiag = x - 1;
        for (unsigned int y = 1; y <= s1len; y++) {
            unsigned int olddiag = column[y];
            unsigned int cost = (s1[y-1] == s2[x-1]) ? 0 : 1;
            
            unsigned int val1 = column[y] + 1;
            unsigned int val2 = column[y-1] + 1;
            unsigned int val3 = lastdiag + cost;
            
            unsigned int min_val = val1 < val2 ? val1 : val2;
            column[y] = min_val < val3 ? min_val : val3;
            
            lastdiag = olddiag;
        }
    }
    
    res.value = column[s1len];
    res.is_success = 1;
    free(column);
    
    return res;
}

#ifdef __cplusplus
}
#endif
