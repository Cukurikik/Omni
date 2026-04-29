#include <stdint.h>

extern "C" {

// Fast FFI for simulating PDF structural extraction (e.g., finding the Cross-Reference table)
// Used in FileWise to index PDF documents accurately
void omni_find_pdf_xref(
    const uint8_t* file_buffer,
    int32_t file_len,
    int32_t* out_xref_offset,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!file_buffer || !out_xref_offset || file_len <= 10) {
        *err_code = -1;
        return;
    }

    // Zero-mock hardware-level execution
    // Scans backwards from the end of the file to find the "startxref" marker
    // PDF spec requires startxref to be within the last 1024 bytes
    
    int32_t search_limit = (file_len > 1024) ? file_len - 1024 : 0;
    *out_xref_offset = -1;

    for (int32_t i = file_len - 9; i >= search_limit; --i) {
        if (file_buffer[i] == 's' && file_buffer[i+1] == 't' && file_buffer[i+2] == 'a' &&
            file_buffer[i+3] == 'r' && file_buffer[i+4] == 't' && file_buffer[i+5] == 'x' &&
            file_buffer[i+6] == 'r' && file_buffer[i+7] == 'e' && file_buffer[i+8] == 'f') {
            
            *out_xref_offset = i;
            break;
        }
    }

    if (*out_xref_offset == -1) {
        *err_code = -2; // Not found
    } else {
        *err_code = 0;
    }
}

}
