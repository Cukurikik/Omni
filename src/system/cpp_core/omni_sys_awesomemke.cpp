#include <cmath>

extern "C" {
    void omni_sys_awesomemke_apply_rank1_update(float* weights, const float* u, const float* v, int rows, int cols, float lr) {
        if (!weights || !u || !v || rows <= 0 || cols <= 0) return;
        
        // Rank-1 update mock: W' = W + lr * (u * v^T)
        for (int i = 0; i < rows; ++i) {
            for (int j = 0; j < cols; ++j) {
                weights[i * cols + j] += lr * u[i] * v[j];
            }
        }
    }
}
