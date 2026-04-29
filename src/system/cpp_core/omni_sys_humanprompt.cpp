#include <cstring>

extern "C" {
    int omni_sys_humanprompt_validate(const char* prompt) {
        if (!prompt) return 0;
        
        // Simple brace balance check for templates
        int depth = 0;
        int len = std::strlen(prompt);
        
        for (int i = 0; i < len; ++i) {
            if (prompt[i] == '{') depth++;
            else if (prompt[i] == '}') depth--;
            
            if (depth < 0) return 0; // Unmatched closing brace
        }
        
        return depth == 0 ? 1 : 0; // Must end with 0 depth
    }
}
