#include <cstdint>

extern "C" {
    uint32_t omni_sys_datacontam_hash(const char* text, int len) {
        if (!text || len <= 0) return 0;
        
        uint32_t hash = 2166136261u; // FNV-1a basis
        for (int i = 0; i < len; ++i) {
            hash ^= (uint8_t)text[i];
            hash *= 16777619u;
        }
        return hash;
    }
}
