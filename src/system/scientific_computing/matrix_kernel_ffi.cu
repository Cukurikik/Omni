#include <stdint.h>

extern "C" {

double omni_gpu_matrix_multiply_flops(int32_t m, int32_t n, int32_t k, int32_t* err_code) {
    if (!err_code) return 0.0;
    
    if (m <= 0 || n <= 0 || k <= 0) {
        *err_code = -1;
        return 0.0;
    }

    // Deterministic simulation of Matrix Multiplication FLOPS (2 * M * N * K)
    double flops = 2.0 * (double)m * (double)n * (double)k;
    
    // Calculate theoretical GFLOPS assuming 1ms execution time
    double gflops = (flops / 1e9) / 0.001; 

    *err_code = 0;
    return gflops;
}

}
