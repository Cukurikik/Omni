#include <cstring>

extern "C" {
    int omni_sys_codegen_indentation_level(const char* line) {
        if (!line) return 0;
        
        int spaces = 0;
        while (line[spaces] == ' ') {
            spaces++;
        }
        
        // 4 spaces = 1 indent level
        return spaces / 4;
    }
}
