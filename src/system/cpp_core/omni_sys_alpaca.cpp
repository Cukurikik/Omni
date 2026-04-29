#include <cstdint>
#include <cmath>

extern "C" {
    /// Compute instruction quality score via token density heuristic.
    float omni_sys_alpaca_instruction_score(const char* instruction, int len) {
        if (!instruction || len <= 0) return 0.0f;
        int unique_chars = 0;
        bool seen[256] = {};
        for (int i = 0; i < len; ++i) {
            unsigned char c = (unsigned char)instruction[i];
            if (!seen[c]) { seen[c] = true; unique_chars++; }
        }
        return (float)unique_chars / (float)len;
    }

    /// Validate instruction-response alignment via length ratio.
    float omni_sys_alpaca_alignment_ratio(int instr_len, int resp_len) {
        if (instr_len <= 0 || resp_len <= 0) return 0.0f;
        float ratio = (float)resp_len / (float)instr_len;
        return (ratio > 0.5f && ratio < 20.0f) ? 1.0f : 0.0f;
    }
}
