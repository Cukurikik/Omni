#include <cstdint>

extern "C" {
    // Radix/Trie structure evaluation for fast sentiment word matching
    // Assumes an extremely simplified dictionary structure where positive=1, negative=-1, neutral=0
    int32_t sentiment_aggregate_score(const int32_t* token_scores, uint32_t count) {
        int32_t total_score = 0;
        int32_t negations = 0; // Flip polarity if "not" is encountered
        
        for (uint32_t i = 0; i < count; ++i) {
            if (token_scores[i] == -999) { // Special code for negation word
                negations ^= 1;
            } else {
                if (negations) {
                    total_score -= token_scores[i];
                    negations = 0; // Reset after applying
                } else {
                    total_score += token_scores[i];
                }
            }
        }
        
        return total_score;
    }
}
