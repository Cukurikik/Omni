#include <cmath>

extern "C" {
    void omni_sys_deco_softmax(float* logits, int size, float temperature) {
        if (size <= 0 || temperature <= 0.0f) return;
        
        float max_val = logits[0];
        for (int i = 1; i < size; ++i) {
            if (logits[i] > max_val) max_val = logits[i];
        }
        
        float sum = 0.0f;
        for (int i = 0; i < size; ++i) {
            logits[i] = std::exp((logits[i] - max_val) / temperature);
            sum += logits[i];
        }
        
        for (int i = 0; i < size; ++i) {
            logits[i] /= sum;
        }
    }
}
