#include <cstdint>

extern "C" {
    // CryptoPredict moving window variance
    float cryptopredict_calculate_variance(const float* prices, uint32_t length) {
        if (length < 2) return 0.0f;
        
        float sum = 0.0f;
        for (uint32_t i = 0; i < length; ++i) sum += prices[i];
        float mean = sum / length;
        
        float var_sum = 0.0f;
        for (uint32_t i = 0; i < length; ++i) {
            float diff = prices[i] - mean;
            var_sum += diff * diff;
        }
        
        return var_sum / length;
    }
}
