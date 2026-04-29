#include <cstdint>

extern "C" {
    void omni_sys_minicpm_quantize_int8(const float* fp32_arr, int8_t* int8_arr, int size, float scale) {
        if (!fp32_arr || !int8_arr || size <= 0) return;
        
        for (int i = 0; i < size; ++i) {
            float val = fp32_arr[i] / scale;
            if (val > 127.0f) val = 127.0f;
            if (val < -128.0f) val = -128.0f;
            int8_arr[i] = (int8_t)val;
        }
    }
}
