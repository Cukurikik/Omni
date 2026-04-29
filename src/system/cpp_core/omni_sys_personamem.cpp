#include <cstring>
#include <string>
#include <vector>

extern "C" {
    int omni_sys_personamem_hash(const char* fact) {
        if (!fact) return 0;
        
        // FNV-1a deterministic hash
        unsigned int hash = 2166136261u;
        int len = std::strlen(fact);
        
        for (int i = 0; i < len; ++i) {
            hash ^= (unsigned char)fact[i];
            hash *= 16777619;
        }
        return hash;
    }
}
