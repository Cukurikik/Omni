#include <cstring>

extern "C" {
    int omni_sys_mlmm_chrf_score(const char* hyp, const char* ref, int n_gram) {
        if (!hyp || !ref || n_gram <= 0) return 0;
        
        // Simplified Character N-Gram match count logic
        int hyp_len = std::strlen(hyp);
        int ref_len = std::strlen(ref);
        
        if (hyp_len < n_gram || ref_len < n_gram) return 0;
        
        int matches = 0;
        for (int i = 0; i <= hyp_len - n_gram; ++i) {
            for (int j = 0; j <= ref_len - n_gram; ++j) {
                if (std::strncmp(hyp + i, ref + j, n_gram) == 0) {
                    matches++;
                    break;
                }
            }
        }
        return matches;
    }
}
