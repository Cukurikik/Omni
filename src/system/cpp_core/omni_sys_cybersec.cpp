#include <cstdint>

extern "C" {
    // CyberSec fast hex decoding for shellcode detection
    bool cybersec_is_hex_encoded_shellcode(const char* text, uint32_t length) {
        uint32_t hex_count = 0;
        for (uint32_t i = 0; i < length - 3; ++i) {
            if (text[i] == '\\' && text[i+1] == 'x') {
                char c1 = text[i+2];
                char c2 = text[i+3];
                bool is_hex1 = (c1 >= '0' && c1 <= '9') || (c1 >= 'a' && c1 <= 'f') || (c1 >= 'A' && c1 <= 'F');
                bool is_hex2 = (c2 >= '0' && c2 <= '9') || (c2 >= 'a' && c2 <= 'f') || (c2 >= 'A' && c2 <= 'F');
                if (is_hex1 && is_hex2) hex_count++;
            }
        }
        return hex_count > 5; // Arbitrary heuristic threshold
    }
}
