#include <cmath>

extern "C" {
    float omni_sys_finance_volatility(const float* prices, int days) {
        if (!prices || days <= 1) return 0.0f;
        
        float mean = 0.0f;
        for (int i = 0; i < days; ++i) mean += prices[i];
        mean /= days;
        
        float variance = 0.0f;
        for (int i = 0; i < days; ++i) {
            float diff = prices[i] - mean;
            variance += diff * diff;
        }
        variance /= (days - 1);
        
        return std::sqrt(variance);
    }
}
