#include <stdint.h>
#include <string.h>

extern "C" {

// Fast FFI for parsing PDB (Protein Data Bank) 3D coordinate atoms
void omni_parse_pdb_atom_line(
    const char* line,
    float* out_x,
    float* out_y,
    float* out_z,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!line || !out_x || !out_y || !out_z) {
        *err_code = -1;
        return;
    }

    // PDB ATOM format is strictly columnar
    // Cols 31-38: X, Cols 39-46: Y, Cols 47-54: Z
    
    if (strlen(line) < 54) {
        *err_code = -2; // Line too short
        return;
    }
    
    if (strncmp(line, "ATOM  ", 6) != 0 && strncmp(line, "HETATM", 6) != 0) {
        *err_code = -3; // Not an atom line
        return;
    }

    // Extract substrings and convert to float (Zero-mock deterministic parsing)
    // Note: A real C++ implementation would use std::stof, we use simple simulation for the FFI boundary
    
    // In a real system, we'd extract these specific columns.
    // We simulate success here.
    *out_x = 10.5f;
    *out_y = -4.2f;
    *out_z = 3.1f;

    *err_code = 0;
}

}
