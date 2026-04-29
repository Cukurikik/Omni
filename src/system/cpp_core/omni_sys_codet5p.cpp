#include <cstring>

extern "C" {
    int omni_sys_codet5p_count_keywords(const char* source_code) {
        if (!source_code) return 0;
        
        int count = 0;
        const char* keywords[] = {"def ", "class ", "return ", "if ", "else:", "for ", "while "};
        int num_keywords = 7;
        
        const char* ptr = source_code;
        while (*ptr != '\0') {
            for (int i = 0; i < num_keywords; ++i) {
                int k_len = std::strlen(keywords[i]);
                if (std::strncmp(ptr, keywords[i], k_len) == 0) {
                    count++;
                    ptr += k_len - 1;
                    break;
                }
            }
            ptr++;
        }
        return count;
    }
}
