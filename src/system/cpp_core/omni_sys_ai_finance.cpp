#include <cstdint>
extern "C" {
    int omni_sys_ai_finance_sharpe_ratio_x1000(const float* returns, int n, float risk_free) {
        if (!returns || n <= 1) return 0;
        float sum = 0, sum2 = 0;
        for (int i = 0; i < n; ++i) { float r = returns[i] - risk_free; sum += r; sum2 += r*r; }
        float mean = sum / (float)n;
        float var = sum2 / (float)n - mean * mean;
        if (var <= 0) return 0;
        return (int)(mean / std::sqrt(var) * 1000.0f);
    }
}
