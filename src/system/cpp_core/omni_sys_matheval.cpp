#include <cstdint>

extern "C" {
    // MathEval exact match heuristic
    bool matheval_verify_exact_match(const char* pred, uint32_t pred_len, const char* truth, uint32_t truth_len) {
        if (pred_len != truth_len) return false;
        for (uint32_t i = 0; i < pred_len; ++i) {
            // Case insensitive and space-agnostic comparison for simple tokens
            char p = pred[i] == ' ' ? '_' : (pred[i] >= 'A' && pred[i] <= 'Z' ? pred[i] + 32 : pred[i]);
            char t = truth[i] == ' ' ? '_' : (truth[i] >= 'A' && truth[i] <= 'Z' ? truth[i] + 32 : truth[i]);
            if (p != t) return false;
        }
        return true;
    }
}
