#include <cmath>

extern "C" {
    void omni_sys_babygpt_softmax(float* logits, int size) {
        if (!logits || size <= 0) return;
        
        float max_logit = logits[0];
        for (int i = 1; i < size; ++i) {
            if (logits[i] > max_logit) max_logit = logits[i];
        }
        
        float sum_exp = 0.0f;
        for (int i = 0; i < size; ++i) {
            logits[i] = std::exp(logits[i] - max_logit);
            sum_exp += logits[i];
        }
        
        for (int i = 0; i < size; ++i) {
            logits[i] /= sum_exp;
        }
    }
}
