#include <cstring>

extern "C" {
    int omni_sys_coauthor_count_macros(const char* latex_doc) {
        if (!latex_doc) return 0;
        
        int macros = 0;
        int len = std::strlen(latex_doc);
        
        for (int i = 0; i < len; ++i) {
            if (latex_doc[i] == '\\' && i + 1 < len && latex_doc[i+1] != '\\') {
                macros++;
            }
        }
        return macros;
    }
}
