#include <cstring>

extern "C" {
    int omni_sys_react_validate_format(const char* output) {
        if (!output) return 0;
        
        // Must contain both Thought: and Action:
        const char* t_ptr = std::strstr(output, "Thought:");
        const char* a_ptr = std::strstr(output, "Action:");
        
        if (t_ptr && a_ptr && (t_ptr < a_ptr)) {
            return 1;
        }
        return 0;
    }
}
