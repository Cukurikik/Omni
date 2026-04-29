#include <cmath>

extern "C" {
    float omni_sys_niutrans_bleu_penalty(int ref_len, int hyp_len) {
        if (hyp_len <= 0) return 0.0f;
        if (hyp_len > ref_len) return 1.0f;
        
        return std::exp(1.0f - ((float)ref_len / (float)hyp_len));
    }
}
