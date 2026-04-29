#include <cstdint>

extern "C" {
    // Detect if a UTF-8 character is in the CJK Unified Ideographs block (4E00 - 9FFF)
    bool is_cjk_ideograph(const uint8_t* utf8_char, uint32_t bytes) {
        if (bytes != 3) return false;
        
        uint32_t codepoint = ((utf8_char[0] & 0x0F) << 12) | 
                             ((utf8_char[1] & 0x3F) << 6) | 
                             (utf8_char[2] & 0x3F);
                             
        return (codepoint >= 0x4E00 && codepoint <= 0x9FFF);
    }
    
    uint32_t chinese_eval_count_cjk_characters(const uint8_t* text, uint32_t length) {
        uint32_t count = 0;
        uint32_t i = 0;
        while (i < length) {
            uint8_t c = text[i];
            uint32_t char_len = 1;
            if ((c & 0xE0) == 0xE0) {
                char_len = 3;
                if (i + 2 < length && is_cjk_ideograph(&text[i], 3)) {
                    count++;
                }
            } else if ((c & 0xC0) == 0xC0) {
                char_len = 2;
            } else if ((c & 0xF0) == 0xF0) {
                char_len = 4;
            }
            i += char_len;
        }
        return count;
    }
}
