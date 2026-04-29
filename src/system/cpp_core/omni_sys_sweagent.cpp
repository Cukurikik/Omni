#include <cstdint>

extern "C" {
    int omni_sys_sweagent_diff_size(const char* old_code, const char* new_code) {
        if (!old_code || !new_code) return -1;
        
        // Super naive diff size calculation
        int old_len = 0; while (old_code[old_len] != '\0') old_len++;
        int new_len = 0; while (new_code[new_len] != '\0') new_len++;
        
        int diff = new_len - old_len;
        return (diff >= 0) ? diff : -diff; // Abs
    }
}
