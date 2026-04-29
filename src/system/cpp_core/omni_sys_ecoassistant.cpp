extern "C" {
    float omni_sys_ecoassistant_score(const char* prompt, int length) {
        if (!prompt || length <= 0) return 0.0f;
        
        // Heuristic complexity scoring based on length and unique chars
        int unique_chars = 0;
        int seen[256] = {0};
        
        for (int i = 0; i < length; ++i) {
            unsigned char c = prompt[i];
            if (seen[c] == 0) {
                seen[c] = 1;
                unique_chars++;
            }
        }
        
        float score = (float)unique_chars / 128.0f + (length / 1000.0f);
        if (score > 1.0f) score = 1.0f;
        
        return score;
    }
}
