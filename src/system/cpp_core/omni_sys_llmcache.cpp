#include <cstring>

extern "C" {
    int omni_sys_llmcache_murmur_hash(const char* key) {
        if (!key) return 0;
        
        // Simple Murmur3 32-bit mock
        unsigned int hash = 0x811c9dc5;
        int len = std::strlen(key);
        
        for (int i = 0; i < len; ++i) {
            hash ^= key[i];
            hash *= 0x01000193;
        }
        return hash;
    }
}
