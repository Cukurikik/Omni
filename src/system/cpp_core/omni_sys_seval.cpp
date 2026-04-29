#include <cstring>

extern "C" {
    int omni_sys_seval_fast_match(const char* text, const char* word) {
        if (!text || !word) return 0;
        
        // Exact substring mock for fast C++ filtering
        const char* p = std::strstr(text, word);
        return p != nullptr ? 1 : 0;
    }
}
