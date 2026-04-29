#include <cstring>

extern "C" {
    int omni_sys_autogeo_keyword_density(const char* text, const char* keyword) {
        if (!text || !keyword) return 0;
        
        int k_len = std::strlen(keyword);
        if (k_len == 0) return 0;
        
        int count = 0;
        const char* ptr = text;
        
        while ((ptr = std::strstr(ptr, keyword)) != nullptr) {
            count++;
            ptr += k_len;
        }
        
        return count;
    }
}
