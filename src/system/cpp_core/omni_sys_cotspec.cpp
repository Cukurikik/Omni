#include <cstring>

extern "C" {
    int omni_sys_cotspec_extract_answer(const char* cot_text, char* out_answer, int max_len) {
        if (!cot_text || !out_answer || max_len <= 0) return 0;
        
        // Find "Therefore, the answer is "
        const char* token = "answer is ";
        const char* ptr = std::strstr(cot_text, token);
        
        if (ptr) {
            ptr += std::strlen(token);
            int i = 0;
            while (ptr[i] != '\0' && ptr[i] != '.' && i < max_len - 1) {
                out_answer[i] = ptr[i];
                i++;
            }
            out_answer[i] = '\0';
            return i;
        }
        
        out_answer[0] = '\0';
        return 0;
    }
}
