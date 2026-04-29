#include <cstdint>

extern "C" {
    // OMNI System Layer - Fast CRC32 computation kernel for compiler tokens
    uint32_t compute_crc32(const uint8_t* data, int32_t length) {
        if (!data || length <= 0) return 0;
        uint32_t crc = 0xFFFFFFFF;
        for (int32_t i = 0; i < length; i++) {
            crc ^= data[i];
            for (int32_t j = 0; j < 8; j++) {
                if (crc & 1) crc = (crc >> 1) ^ 0xEDB88320;
                else crc >>= 1;
            }
        }
        return crc ^ 0xFFFFFFFF;
    }
}
