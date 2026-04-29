#include <cstring>

extern "C" {
    int omni_sys_hackgpt_ansi_strip(const char* input, char* output, int max_len) {
        if (!input || !output || max_len <= 0) return 0;
        
        int in_idx = 0;
        int out_idx = 0;
        int in_escape = 0;
        
        while (input[in_idx] != '\0' && out_idx < max_len - 1) {
            if (input[in_idx] == '\033') {
                in_escape = 1;
            } else if (in_escape && input[in_idx] == 'm') {
                in_escape = 0;
            } else if (!in_escape) {
                output[out_idx++] = input[in_idx];
            }
            in_idx++;
        }
        
        output[out_idx] = '\0';
        return out_idx;
    }
}
