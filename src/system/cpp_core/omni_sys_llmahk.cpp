#include <cstring>

extern "C" {
    int omni_sys_llmahk_validate_hotkey(const char* hotkey) {
        if (!hotkey) return 0;
        
        // Mock valid AHK hotkey format e.g., ^j::
        int len = std::strlen(hotkey);
        if (len > 3 && hotkey[len-1] == ':' && hotkey[len-2] == ':') {
            return 1; // Valid
        }
        return 0; // Invalid
    }
}
