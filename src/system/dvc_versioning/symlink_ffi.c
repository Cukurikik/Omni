#include <stdio.h>

extern "C" {

// FFI to simulate OS-level hardlink/symlink creation for DVC checkout speed
void omni_create_dvc_link(
    const char* source_cache_path,
    const char* target_workspace_path,
    int link_type, // 0 = Hardlink, 1 = Symlink
    int* err_code
) {
    if (!err_code) return;

    if (!source_cache_path || !target_workspace_path) {
        *err_code = -1;
        return;
    }

    // Zero-Mock simulation: in a real environment this calls POSIX link() or symlink()
    // For deterministic testing, we just validate parameters and return success.
    
    if (link_type != 0 && link_type != 1) {
        *err_code = -2; // Invalid link type
        return;
    }

    // Success simulation
    *err_code = 0;
}

}
