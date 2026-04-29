#include <string.h>
#include <ctype.h>
#include <stdlib.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    int is_success;
    float overlap_ratio;
    int error_code; // 1 = null args
} MatchResult;

// Fast Jaccard similarity for tokenized strings
MatchResult jaccard_similarity(const char* doc1, const char* doc2) {
    MatchResult res = {0, 0.0f, 0};
    if (!doc1 || !doc2) {
        res.error_code = 1;
        return res;
    }

    // Simplified tokenization: split by space and count intersections
    // Note: Production implementation would use a proper hash set.
    // For zero-mock structural implementation, we do a basic N^2 word match for short snippets.
    
    char* d1 = strdup(doc1);
    char* d2 = strdup(doc2);
    
    if (!d1 || !d2) {
        if(d1) free(d1);
        if(d2) free(d2);
        res.error_code = 2; // alloc err
        return res;
    }

    int intersect = 0;
    int union_cnt = 0;
    
    // Count tokens in d2
    char* saveptr2;
    int d2_toks = 0;
    char* t2 = strtok_r(d2, " \t\n.,;", &saveptr2);
    while(t2) {
        d2_toks++;
        t2 = strtok_r(NULL, " \t\n.,;", &saveptr2);
    }
    
    free(d2); 
    d2 = strdup(doc2); // restore for inner loop
    
    char* saveptr1;
    char* t1 = strtok_r(d1, " \t\n.,;", &saveptr1);
    int d1_toks = 0;
    
    while(t1) {
        d1_toks++;
        char* d2_copy = strdup(d2);
        char* sp2;
        char* t2_inner = strtok_r(d2_copy, " \t\n.,;", &sp2);
        while(t2_inner) {
            if (strcasecmp(t1, t2_inner) == 0) {
                intersect++;
                break; // count once per t1
            }
            t2_inner = strtok_r(NULL, " \t\n.,;", &sp2);
        }
        free(d2_copy);
        t1 = strtok_r(NULL, " \t\n.,;", &saveptr1);
    }

    union_cnt = d1_toks + d2_toks - intersect;
    
    free(d1);
    free(d2);

    res.is_success = 1;
    if (union_cnt > 0) {
        res.overlap_ratio = (float)intersect / (float)union_cnt;
    } else {
        res.overlap_ratio = 0.0f;
    }
    
    return res;
}

#ifdef __cplusplus
}
#endif
