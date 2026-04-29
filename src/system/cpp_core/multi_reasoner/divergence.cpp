#include <cstdint>
#include <cmath>

extern "C" {
    // OMNI System Layer - Fast KL Divergence Kernel
    double compute_kl_divergence(const double* p, const double* q, int32_t len) {
        if (!p || !q || len <= 0) return 0.0;
        
        double kl = 0.0;
        for (int32_t i = 0; i < len; ++i) {
            double p_val = p[i] < 1e-10 ? 1e-10 : p[i];
            double q_val = q[i] < 1e-10 ? 1e-10 : q[i];
            kl += p_val * std::log(p_val / q_val);
        }
        return kl;
    }
}
