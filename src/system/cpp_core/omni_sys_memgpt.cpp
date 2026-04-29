#include <cstring>

extern "C" {
    int omni_sys_memgpt_paginate(const char* text, int page_size, int page_num, char* output) {
        if (!text || !output || page_size <= 0 || page_num < 0) return 0;
        
        int len = std::strlen(text);
        int start_idx = page_num * page_size;
        
        if (start_idx >= len) {
            output[0] = '\0';
            return 0;
        }
        
        int copy_len = len - start_idx;
        if (copy_len > page_size) copy_len = page_size;
        
        std::strncpy(output, text + start_idx, copy_len);
        output[copy_len] = '\0';
        return copy_len;
    }
}
