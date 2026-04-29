#include <cstdint>
#include <cmath>

// OMNI System Kernel: CRC32
extern "C" {
        uint32_t compute(const uint8_t* data, int32_t len) {
            uint32_t crc = 0xFFFFFFFF;
            for(int i=0; i<len; i++) {
                crc ^= data[i];
                for(int j=0; j<8; j++) {
                    crc = (crc & 1) ? (crc >> 1) ^ 0xEDB88320 : crc >> 1;
                }
            }
            return ~crc;
        }
}