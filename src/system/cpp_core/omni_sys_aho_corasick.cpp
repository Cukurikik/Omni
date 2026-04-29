#include <cmath>
extern "C" {
    int omni_sys_aho_corasick_build_goto(const char* pattern, int plen, int* goto_table, int max_states) {
        if (!pattern || plen <= 0 || !goto_table) return 0;
        int state = 0;
        for (int i = 0; i < plen && state < max_states - 1; ++i) {
            goto_table[state] = (int)(unsigned char)pattern[i];
            state++;
        }
        return state;
    }
}
