#include <cmath>

extern "C" {
    float omni_sys_puzzletest_entropy(const float* probabilities, int size) {
        if (!probabilities || size <= 0) return 0.0f;
        
        float entropy = 0.0f;
        for (int i = 0; i < size; ++i) {
            if (probabilities[i] > 0.0f) {
                entropy -= probabilities[i] * std::log2(probabilities[i]);
            }
        }
        return entropy;
    }
}
