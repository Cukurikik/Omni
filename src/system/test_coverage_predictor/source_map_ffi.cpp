#include <stdint.h>

extern "C" {

// Fast FFI for source map alignment
// Aligns transpiled/compiled line numbers back to original source code line numbers
// Essential for accurate test coverage reporting in multi-language OMNI projects
void omni_align_source_map(
    const int32_t* compiled_lines,
    const int32_t* original_lines,
    int32_t map_size,
    int32_t query_compiled_line,
    int32_t* out_original_line,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!compiled_lines || !original_lines || !out_original_line || map_size <= 0) {
        *err_code = -1;
        return;
    }

    // Zero-mock hardware-level execution
    // Simple linear scan for simulation. Binary search would be used if sorted.
    *out_original_line = -1; // Default not found

    for (int32_t i = 0; i < map_size; ++i) {
        if (compiled_lines[i] == query_compiled_line) {
            *out_original_line = original_lines[i];
            break;
        }
    }

    *err_code = 0;
}

}
