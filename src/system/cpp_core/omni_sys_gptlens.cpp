#include <cstdint>

extern "C" {
    int omni_sys_gptlens_detect_reentrancy(const char* code, int len) {
        if (!code || len <= 0) return 0;
        
        // Mock C++ static analysis for reentrancy (call.value)
        const char* call_value = ".call{value:";
        const char* p = code;
        while ((p = __builtin_strstr(p, call_value)) != nullptr) {
            return 1; // Potential reentrancy detected
        }
        return 0;
    }
}
