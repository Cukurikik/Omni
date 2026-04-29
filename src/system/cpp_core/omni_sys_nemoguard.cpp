#include <cstring>

extern "C" {
    int omni_sys_nemoguard_jailbreak_score(const char* text, int len) {
        if (!text || len <= 0) return 0;
        
        // Mock jailbreak scoring logic counting unusual characters
        int penalty = 0;
        for(int i=0; i<len; ++i) {
            if(text[i] == '<' || text[i] == '>' || text[i] == '$') {
                penalty += 10;
            }
        }
        return penalty; // Higher means higher risk
    }
}
