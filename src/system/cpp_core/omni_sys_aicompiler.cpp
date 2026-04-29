#include <cmath>

extern "C" {
    float omni_sys_aicompiler_loop_unroll_factor(int loop_iters, int reg_count) {
        if (loop_iters <= 0 || reg_count <= 0) return 1.0f;
        
        // Simple heuristic for unroll factor based on available registers
        int factor = reg_count / 4;
        if (factor > loop_iters) factor = loop_iters;
        if (factor > 16) factor = 16; // Max unroll cap
        
        return (float)factor;
    }
}
