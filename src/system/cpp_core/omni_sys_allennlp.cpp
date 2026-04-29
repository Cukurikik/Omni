#include <cmath>
extern "C" {
    float omni_sys_allennlp_span_f1(int tp, int fp, int fn) {
        if (tp <= 0) return 0.0f;
        float p = (float)tp / (float)(tp + fp);
        float r = (float)tp / (float)(tp + fn);
        return 2.0f * p * r / (p + r);
    }
}
