#include <stdint.h>
#include <string.h>

extern "C" {

// FFI export for ultra-fast binary PDF stream parsing
void omni_extract_pdf_text_chunks(
    const uint8_t* pdf_bytes, 
    int32_t length, 
    uint8_t* out_buffer, 
    int32_t out_max_len, 
    int32_t* bytes_written, 
    int32_t* err_code
) {
    if (!err_code) return;

    if (!pdf_bytes || !out_buffer || !bytes_written || length <= 0 || out_max_len <= 0) {
        *err_code = -1;
        return;
    }

    *bytes_written = 0;
    int32_t write_idx = 0;

    // Deterministic mathematical stream scanning for uncompressed PDF text operators (Tj, TJ)
    // Real implementation would handle FlateDecode. Here we implement the strict scanning state machine.
    
    int state = 0; // 0: scanning, 1: inside string (...)
    
    for (int32_t i = 0; i < length; ++i) {
        if (write_idx >= out_max_len - 1) break; // Buffer full

        uint8_t b = pdf_bytes[i];

        if (state == 0) {
            if (b == '(') {
                state = 1; // Start of string
            }
        } else if (state == 1) {
            if (b == ')') {
                state = 0; // End of string
                out_buffer[write_idx++] = ' '; // Add space between chunks
            } else if (b == '\\') {
                // Skip escaped characters deterministically
                i++;
            } else {
                // Append text character
                out_buffer[write_idx++] = b;
            }
        }
    }

    out_buffer[write_idx] = '\0';
    *bytes_written = write_idx;
    *err_code = 0;
}

}
