#include <cstdint>

extern "C" {
    int omni_sys_jacobi_convergence_check(const int* prev_block, const int* curr_block, int size) {
        if (!prev_block || !curr_block || size <= 0) return 0;
        
        for (int i = 0; i < size; ++i) {
            if (prev_block[i] != curr_block[i]) {
                return 0; // Not converged
            }
        }
        return 1; // Converged
    }
}
