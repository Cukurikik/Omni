#include <cstdint>

extern "C" {
    int omni_sys_mllmcolab_vram_check(int required_mb, int available_mb) {
        if (required_mb <= 0 || available_mb <= 0) return 0; // Fail
        
        // 10% buffer for CUDA context overhead
        int overhead = required_mb / 10;
        
        if (required_mb + overhead <= available_mb) {
            return 1; // Success
        }
        return 0; // Fail
    }
}
