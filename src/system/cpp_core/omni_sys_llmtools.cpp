#include <cstdint>
#include <algorithm>

extern "C" {
    // LLM tools fast parameter calculation
    uint64_t compute_llm_parameter_memory_bytes(uint64_t params, uint8_t bytes_per_param) {
        return params * bytes_per_param;
    }

    uint64_t compute_kv_cache_bytes(uint32_t seq_len, uint32_t batch_size, uint32_t hidden_size, uint16_t num_layers, uint8_t bytes_per_element) {
        // 2 for Key and Value
        return 2ULL * seq_len * batch_size * hidden_size * num_layers * bytes_per_element;
    }
}
