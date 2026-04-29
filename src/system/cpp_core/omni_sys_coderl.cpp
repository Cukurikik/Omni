#include <cstring>

extern "C" {
    int omni_sys_coderl_ast_depth(const char* source_code) {
        if (!source_code) return 0;
        
        int current_depth = 0;
        int max_depth = 0;
        int len = std::strlen(source_code);
        
        // Simple deterministic depth checker based on braces
        for (int i = 0; i < len; ++i) {
            if (source_code[i] == '{') {
                current_depth++;
                if (current_depth > max_depth) {
                    max_depth = current_depth;
                }
            } else if (source_code[i] == '}') {
                current_depth--;
                if (current_depth < 0) current_depth = 0; // Malformed resilience
            }
        }
        
        return max_depth;
    }
}
