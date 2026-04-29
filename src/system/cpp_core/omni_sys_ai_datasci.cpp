#include <cmath>
extern "C" {
    float omni_sys_ai_datasci_team_pearson_r(const float* x, const float* y, int n) {
        if (!x || !y || n <= 1) return 0.0f;
        float sx = 0, sy = 0, sxy = 0, sx2 = 0, sy2 = 0;
        for (int i = 0; i < n; ++i) {
            sx += x[i]; sy += y[i]; sxy += x[i]*y[i]; sx2 += x[i]*x[i]; sy2 += y[i]*y[i];
        }
        float num = (float)n * sxy - sx * sy;
        float den = std::sqrt(((float)n * sx2 - sx*sx) * ((float)n * sy2 - sy*sy));
        return den > 0 ? num / den : 0.0f;
    }
}
