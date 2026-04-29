#include <cstdint>

extern "C" {

double omni_allocate_kv_cache(int32_t sequence_length, int32_t* err_code) {
    if (!err_code) return 0.0;
    
    if (sequence_length <= 0) {
        *err_code = -1;
        return 0.0;
    }

    // Mathematical representation of KV cache size 
    // Example: (seq_len * hidden_size * num_layers * 2(K,V) * 2 bytes(FP16))
    double hidden_size = 768.0;
    double num_layers = 12.0;
    
    double bytes_allocated = (double)sequence_length * hidden_size * num_layers * 4.0;
    
    *err_code = 0;
    return bytes_allocated / (1024.0 * 1024.0); // Return MBs
}

}
