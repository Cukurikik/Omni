#include <cstdint>

extern "C" {
    // Fast JSON brace validator for deployment manifests
    bool langforge_validate_manifest_braces(const char* json_data, uint32_t length) {
        int32_t curley = 0;
        int32_t square = 0;
        bool in_string = false;
        bool escape = false;
        
        for (uint32_t i = 0; i < length; ++i) {
            char c = json_data[i];
            
            if (escape) {
                escape = false;
                continue;
            }
            
            if (c == '\\') {
                escape = true;
            } else if (c == '"') {
                in_string = !in_string;
            } else if (!in_string) {
                if (c == '{') curley++;
                else if (c == '}') curley--;
                else if (c == '[') square++;
                else if (c == ']') square--;
                
                if (curley < 0 || square < 0) return false;
            }
        }
        
        return curley == 0 && square == 0 && !in_string;
    }
}
