#include <cstring>

extern "C" {
    int omni_sys_ultrachat_diversity_hash(const char* text, int len) {
        if (!text || len <= 0) return 0;
        
        // Simple hash to bucket responses for diversity checking
        unsigned int hash = 5381;
        for (int i = 0; i < len; ++i) {
            hash = ((hash << 5) + hash) + text[i];
        }
        return hash % 1024;
    }
}
