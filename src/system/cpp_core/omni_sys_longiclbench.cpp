#include <cstdint>

extern "C" {
    int omni_sys_longiclbench_count_tokens(const char* text, int len) {
        if (!text || len <= 0) return 0;
        
        int tokens = 0;
        for (int i = 0; i < len; ++i) {
            if (text[i] == ' ' || text[i] == '\\n') {
                tokens++;
            }
        }
        return tokens + 1; // Basic whitespace tokenizer mock
    }
}
