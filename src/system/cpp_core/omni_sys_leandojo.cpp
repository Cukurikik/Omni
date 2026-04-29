#include <cstring>

extern "C" {
    int omni_sys_leandojo_check_syntax(const char* tactic) {
        if (!tactic) return 0;
        
        // Ensure tactic doesn't contain illegal characters for Lean
        int len = std::strlen(tactic);
        for (int i = 0; i < len; ++i) {
            if (tactic[i] == ';' || tactic[i] == '$') {
                return 0; // Illegal
            }
        }
        return 1;
    }
}
