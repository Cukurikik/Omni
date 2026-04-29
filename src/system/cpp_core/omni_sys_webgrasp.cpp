#include <cstring>

extern "C" {
    int omni_sys_webgrasp_xpath_match(const char* xpath, const char* target_tag) {
        if (!xpath || !target_tag) return 0;
        
        // Fast substring check for tag in xpath
        const char* found = std::strstr(xpath, target_tag);
        if (found != nullptr) {
            return 1;
        }
        return 0;
    }
}
