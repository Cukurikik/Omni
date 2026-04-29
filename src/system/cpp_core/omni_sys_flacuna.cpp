#include <cstdint>

extern "C" {
    int omni_sys_flacuna_complexity_estimate(const char* problem_text, int len) {
        if (!problem_text || len <= 0) return 0;
        
        int complexity = 0;
        for (int i = 0; i < len; ++i) {
            // Count logical operators as complexity
            if (problem_text[i] == '?' || problem_text[i] == '=') {
                complexity++;
            }
        }
        return complexity;
    }
}
