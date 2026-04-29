#include <cstring>

extern "C" {
    int omni_sys_langstruct_validate_json_brackets(const char* text) {
        if (!text) return 0;
        
        int open_count = 0;
        int close_count = 0;
        
        int len = std::strlen(text);
        for (int i = 0; i < len; ++i) {
            if (text[i] == '{') open_count++;
            if (text[i] == '}') close_count++;
        }
        
        // Basic bracket balance check
        return (open_count > 0 && open_count == close_count) ? 1 : 0;
    }
}
