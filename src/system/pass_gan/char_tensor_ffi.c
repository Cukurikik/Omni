#include <stdint.h>
#include <stddef.h>

extern "C" {

// FFI export for deterministic mapping of character strings to one-hot tensor representations
void omni_char_to_tensor(
    const char* passwords, 
    int32_t num_passwords, 
    int32_t max_len, 
    int32_t vocab_size, 
    float* out_tensor, 
    int32_t* err_code
) {
    if (!err_code) return;

    if (!passwords || !out_tensor || num_passwords <= 0 || max_len <= 0 || vocab_size <= 0) {
        *err_code = -1;
        return;
    }

    // Initialize tensor to 0 mathematically
    int32_t total_elements = num_passwords * max_len * vocab_size;
    for (int32_t i = 0; i < total_elements; ++i) {
        out_tensor[i] = 0.0f;
    }

    for (int32_t p = 0; p < num_passwords; ++p) {
        for (int32_t l = 0; l < max_len; ++l) {
            char c = passwords[p * max_len + l];
            
            // Null terminator implies padding (mapped to index 0)
            int32_t char_idx = 0;
            if (c != '\0') {
                char_idx = (int32_t)c % vocab_size; // Basic deterministic mapping
            }

            // Calculate 3D tensor offset: [p][l][char_idx]
            int32_t offset = (p * max_len * vocab_size) + (l * vocab_size) + char_idx;
            out_tensor[offset] = 1.0f; // Set one-hot
            
            if (c == '\0') {
                break; // Stop processing this password, rest is padding
            }
        }
    }

    *err_code = 0;
}

}
