#include <cstring>
#include <cstdint>

extern "C" {
    int omni_sys_llmjs_serialize(const char* key, const char* value, char* buffer, int max_len) {
        if (!key || !value || !buffer || max_len <= 0) return -1;
        
        // Simple manual JSON serialization for one KV pair
        int k_len = std::strlen(key);
        int v_len = std::strlen(value);
        
        if (k_len + v_len + 8 > max_len) return -1; // "key":"value",
        
        int pos = 0;
        buffer[pos++] = '\"';
        std::memcpy(buffer + pos, key, k_len); pos += k_len;
        buffer[pos++] = '\"';
        buffer[pos++] = ':';
        buffer[pos++] = '\"';
        std::memcpy(buffer + pos, value, v_len); pos += v_len;
        buffer[pos++] = '\"';
        buffer[pos] = '\0';
        
        return pos;
    }
}
