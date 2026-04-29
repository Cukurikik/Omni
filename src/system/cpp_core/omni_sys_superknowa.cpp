#include <cstring>

extern "C" {
    int omni_sys_superknowa_bm25_mock(const char* query, const char* document) {
        // Very basic mock for BM25 term frequency check
        if (!query || !document) return 0;
        
        int match_count = 0;
        int doc_len = std::strlen(document);
        int query_len = std::strlen(query);
        
        if (query_len == 0 || doc_len == 0) return 0;
        
        // Count rough occurrences of first char as a dummy heuristic
        for (int i = 0; i < doc_len; ++i) {
            if (document[i] == query[0]) match_count++;
        }
        return match_count;
    }
}
