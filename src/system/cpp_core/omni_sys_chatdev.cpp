#include <cstdint>

extern "C" {
    int omni_sys_chatdev_loc_counter(const char* code) {
        if (!code) return 0;
        
        int lines = 0;
        int i = 0;
        while (code[i] != '\0') {
            if (code[i] == '\n') {
                lines++;
            }
            i++;
        }
        // Count last line if not empty
        if (i > 0 && code[i-1] != '\n') {
            lines++;
        }
        return lines;
    }
}
