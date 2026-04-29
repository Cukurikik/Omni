#include <cstdint>
extern "C" {
    uint32_t omni_sys_a2summ_keyword_hash(const char* word, int len) {
        uint32_t h = 0; for (int i = 0; i < len; ++i) h = h * 31 + (uint8_t)word[i]; return h;
    }
    float omni_sys_a2summ_rouge_l(int lcs_len, int ref_len, int hyp_len) {
        if (ref_len <= 0 || hyp_len <= 0) return 0.0f;
        float p = (float)lcs_len / (float)hyp_len;
        float r = (float)lcs_len / (float)ref_len;
        return (p + r > 0) ? 2.0f * p * r / (p + r) : 0.0f;
    }
}
