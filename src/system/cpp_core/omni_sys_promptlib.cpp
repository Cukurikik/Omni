#include <cstdint>

extern "C" {
    int omni_sys_promptlib_token_estimate(int char_count) {
        if (char_count <= 0) return 0;
        
        // Standard heuristic: 1 token ~= 4 chars in English
        return char_count / 4 + 1;
    }
}
