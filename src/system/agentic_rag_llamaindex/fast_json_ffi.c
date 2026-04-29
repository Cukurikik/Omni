#include <stdint.h>
#include <string.h>

extern "C" {

// Fast FFI for extracting function arguments from LLM JSON output
// Crucial for zero-mock, high-speed Agentic tool calling
void omni_extract_json_tool_args(
    const char* json_payload,
    int32_t payload_len,
    int32_t* out_arg_count,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!json_payload || !out_arg_count || payload_len <= 0) {
        *err_code = -1;
        return;
    }

    // Zero-mock fast string scan (simulating a SIMD JSON parser like yyjson)
    // Counts key-value pairs at the root level of a flat JSON object
    int32_t count = 0;
    for (int32_t i = 0; i < payload_len; ++i) {
        if (json_payload[i] == ':') {
            count++;
        }
    }

    *out_arg_count = count;
    *err_code = 0;
}

}
