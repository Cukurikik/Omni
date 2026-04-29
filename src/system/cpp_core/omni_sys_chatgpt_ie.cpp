#include <cstring>

extern "C" {
    int omni_sys_chatgpt_ie_match(const char* text, const char* target) {
        if (!text || !target) return -1;
        
        int text_len = std::strlen(text);
        int target_len = std::strlen(target);
        if (target_len == 0 || text_len < target_len) return 0;

        int matches = 0;
        for (int i = 0; i <= text_len - target_len; ++i) {
            if (std::strncmp(text + i, target, target_len) == 0) {
                matches++;
                i += target_len - 1;
            }
        }
        return matches;
    }
}
