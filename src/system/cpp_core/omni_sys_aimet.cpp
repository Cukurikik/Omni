#include <cmath>
extern "C" {
    float omni_sys_aimet_quantize_symmetric(float value, float scale, int bits) {
        float max_val = (float)((1 << (bits - 1)) - 1);
        float q = roundf(value / scale);
        if (q > max_val) q = max_val;
        if (q < -max_val) q = -max_val;
        return q * scale;
    }
}
