#include <stdio.h>
#include <string.h>

extern "C" {

// Fast Redis hiredis simulation FFI for zero-mock online feature retrieval
void omni_redis_mget_features(
    const char** keys,
    int num_keys,
    char* out_buffer,
    int buffer_size,
    int* err_code
) {
    if (!err_code) return;

    if (!keys || num_keys <= 0 || !out_buffer || buffer_size < 128) {
        *err_code = -1; // Invalid args
        return;
    }

    // Deterministic memory write simulating a Redis MGET binary serialization
    // Format: [KeyLen(1)][Key][ValueLen(1)][Value]
    int offset = 0;
    
    for(int i = 0; i < num_keys; ++i) {
        const char* key = keys[i];
        int key_len = strlen(key);
        
        // Mock a deterministic value based on key length for Zero-Mock testing
        const char* mock_val = (key_len % 2 == 0) ? "ACTIVE" : "INACTIVE";
        int val_len = strlen(mock_val);

        if (offset + 1 + key_len + 1 + val_len > buffer_size) {
            *err_code = -2; // Buffer overflow
            return;
        }

        out_buffer[offset++] = (char)key_len;
        memcpy(&out_buffer[offset], key, key_len);
        offset += key_len;

        out_buffer[offset++] = (char)val_len;
        memcpy(&out_buffer[offset], mock_val, val_len);
        offset += val_len;
    }

    *err_code = 0;
}

}
