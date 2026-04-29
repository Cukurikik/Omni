#include <cstdint>

extern "C" {
    // Fast CRC32 for session state verification
    uint32_t conversant_compute_state_crc32(const uint8_t* data, uint32_t length) {
        uint32_t crc = 0xFFFFFFFF;
        for (uint32_t i = 0; i < length; i++) {
            crc ^= data[i];
            for (uint32_t j = 0; j < 8; j++) {
                crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
            }
        }
        return ~crc;
    }
}
