#include <cmath>
extern "C" {
    float omni_sys_amazon_finance_bollinger_upper(float sma, float std_dev, float k) {
        return sma + k * std_dev;
    }
    float omni_sys_amazon_finance_bollinger_lower(float sma, float std_dev, float k) {
        return sma - k * std_dev;
    }
    float omni_sys_amazon_finance_ema(float price, float prev_ema, float alpha) {
        return alpha * price + (1.0f - alpha) * prev_ema;
    }
}
