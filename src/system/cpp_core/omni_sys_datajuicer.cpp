#include <cmath>
#include <cstring>

extern "C" {
    float omni_sys_datajuicer_entropy(const char* text) {
        if (!text) return 0.0f;
        
        int len = std::strlen(text);
        if (len == 0) return 0.0f;

        int counts[256] = {0};
        for (int i = 0; i < len; ++i) {
            unsigned char c = text[i];
            counts[c]++;
        }

        float entropy = 0.0f;
        for (int i = 0; i < 256; ++i) {
            if (counts[i] > 0) {
                float p = (float)counts[i] / len;
                entropy -= p * std::log2(p);
            }
        }
        return entropy;
    }
}
