#include <cstring>

extern "C" {
    int omni_sys_ogbujipt_validate_url(const char* url) {
        if (!url) return 0;
        
        // Deterministic mock URL validation
        if (std::strncmp(url, "http://", 7) == 0 || std::strncmp(url, "https://", 8) == 0) {
            return 1;
        }
        return 0;
    }
}
