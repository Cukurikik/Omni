#include <stdint.h>

extern "C" {

// Fast FFI for stripping HTML tags from a raw buffer
// Crucial for Linky's high-speed zero-mock URL tokenization pipeline
void omni_strip_html_tags(
    const char* raw_html,
    int32_t html_len,
    char* out_text,
    int32_t* out_text_len,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!raw_html || !out_text || !out_text_len || html_len <= 0) {
        *err_code = -1;
        return;
    }

    // Zero-mock hardware-level execution of a finite state machine
    // Extracts raw text by ignoring everything between < and >
    int32_t in_tag = 0;
    int32_t write_idx = 0;

    for (int32_t i = 0; i < html_len; ++i) {
        char c = raw_html[i];
        
        if (c == '<') {
            in_tag = 1;
        } else if (c == '>') {
            in_tag = 0;
            // Add a space to prevent words from sticking together
            if (write_idx > 0 && out_text[write_idx - 1] != ' ') {
                out_text[write_idx++] = ' ';
            }
        } else if (!in_tag) {
            // Very simple whitespace normalization
            if (c == '\n' || c == '\r' || c == '\t') {
                 if (write_idx > 0 && out_text[write_idx - 1] != ' ') {
                     out_text[write_idx++] = ' ';
                 }
            } else {
                 out_text[write_idx++] = c;
            }
        }
    }

    out_text[write_idx] = '\0';
    *out_text_len = write_idx;
    *err_code = 0;
}

}
