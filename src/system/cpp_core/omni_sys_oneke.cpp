#include <cstdint>
#include <string>
#include <vector>

extern "C" {
    // OneKE entity boundary fast-matching using a simple Aho-Corasick-like state or substring search
    bool fast_entity_match(const char* text, uint32_t text_len, const char* entity, uint32_t entity_len) {
        if (entity_len == 0 || text_len < entity_len) return false;
        
        for (uint32_t i = 0; i <= text_len - entity_len; ++i) {
            bool match = true;
            for (uint32_t j = 0; j < entity_len; ++j) {
                if (text[i + j] != entity[j]) {
                    match = false;
                    break;
                }
            }
            if (match) return true;
        }
        return false;
    }
}
