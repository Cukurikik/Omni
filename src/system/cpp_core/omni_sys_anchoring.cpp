#include <cmath>
extern "C" {
    void omni_sys_anchoring_pipeline_softmax(float* logits, int n) {
        if (!logits || n <= 0) return;
        float mx = logits[0];
        for (int i = 1; i < n; ++i) if (logits[i] > mx) mx = logits[i];
        float sum = 0;
        for (int i = 0; i < n; ++i) { logits[i] = std::exp(logits[i] - mx); sum += logits[i]; }
        for (int i = 0; i < n; ++i) logits[i] /= sum;
    }
}
