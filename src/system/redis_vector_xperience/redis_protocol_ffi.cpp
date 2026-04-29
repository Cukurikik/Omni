#include <stdint.h>
#include <string.h>

extern "C" {

// Fast FFI for parsing Redis Serialization Protocol (RESP3) arrays
// Essential for zero-mock, high-throughput Redis Vector DB communication
void omni_redis_parse_resp_array(
    const char* payload,
    int32_t payload_len,
    int32_t* out_array_size,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!payload || !out_array_size || payload_len <= 0) {
        *err_code = -1;
        return;
    }

    // RESP arrays start with '*' followed by the number of elements and '\r\n'
    if (payload[0] != '*') {
        *err_code = -2; // Protocol error
        return;
    }

    // Deterministic parsing of the array size
    int32_t size = 0;
    int32_t i = 1;
    while (i < payload_len && payload[i] != '\r') {
        if (payload[i] >= '0' && payload[i] <= '9') {
            size = (size * 10) + (payload[i] - '0');
        } else {
            *err_code = -3; // Invalid char in size
            return;
        }
        i++;
    }

    *out_array_size = size;
    *err_code = 0;
}

}
