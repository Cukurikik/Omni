#include <cstring>

extern "C" {
    int omni_sys_halluqa_ngram(const char* text, const char* target_ngram, int ngram_len) {
        if (!text || !target_ngram || ngram_len <= 0) return 0;
        
        int text_len = std::strlen(text);
        if (text_len < ngram_len) return 0;

        int count = 0;
        for (int i = 0; i <= text_len - ngram_len; ++i) {
            if (std::strncmp(text + i, target_ngram, ngram_len) == 0) {
                count++;
            }
        }
        return count;
    }
}
