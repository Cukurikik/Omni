#include <cstdint>

extern "C" {
    /// Match YARA-like byte pattern in APK binary header.
    int omni_sys_apkid_match_magic(const uint8_t* data, int len, uint32_t magic) {
        if (!data || len < 4) return 0;
        uint32_t header = ((uint32_t)data[0] << 24) | ((uint32_t)data[1] << 16) |
                          ((uint32_t)data[2] << 8) | (uint32_t)data[3];
        return header == magic ? 1 : 0;
    }

    /// Compute entropy of a byte buffer for packer detection.
    float omni_sys_apkid_byte_entropy(const uint8_t* data, int len) {
        if (!data || len <= 0) return 0.0f;
        int freq[256] = {};
        for (int i = 0; i < len; ++i) freq[data[i]]++;
        float entropy = 0.0f;
        for (int i = 0; i < 256; ++i) {
            if (freq[i] > 0) {
                float p = (float)freq[i] / (float)len;
                entropy -= p * std::log2(p);
            }
        }
        return entropy;
    }
}
