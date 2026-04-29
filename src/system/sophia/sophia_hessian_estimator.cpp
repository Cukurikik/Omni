// Sophia Optimizer — Diagonal Hessian Estimator (Gauss-Newton-Bartlett)
// RAII-managed buffer for second-order curvature estimation
#include <cstdint>
#include <cmath>
#include <vector>
#include <string>

struct OmniResult { bool is_ok; double value; std::string error; };

class HessianEstimator {
    static constexpr uint32_t MAX_PARAMS = 100000000; // 100M
    static constexpr double MAX_RHO = 100.0;

    std::vector<double> hessian_diag_;
    uint32_t num_params_;
    double rho_;

public:
    static OmniResult create(uint32_t num_params, double rho) {
        if (num_params > MAX_PARAMS) return {false, 0, "Params exceed 100M"};
        if (rho <= 0 || rho > MAX_RHO) return {false, 0, "Rho out of bounds (0, 100]"};
        return {true, static_cast<double>(num_params), ""};
    }

    HessianEstimator(uint32_t np, double rho)
        : hessian_diag_(np, 0.0), num_params_(np), rho_(rho) {}

    // Sophia-H: EMA update of diagonal Hessian
    OmniResult update_ema(const double* grad_sq, uint32_t len, double beta2) {
        if (!grad_sq) return {false, 0, "Null gradient pointer"};
        if (len != num_params_) return {false, 0, "Length mismatch"};
        if (beta2 <= 0 || beta2 >= 1.0) return {false, 0, "beta2 must be in (0,1)"};
        for (uint32_t i = 0; i < len; i++) {
            if (std::isnan(grad_sq[i])) return {false, 0, "NaN in gradient"};
            hessian_diag_[i] = beta2 * hessian_diag_[i] + (1.0 - beta2) * grad_sq[i];
        }
        return {true, 1.0, ""};
    }

    // Sophia clipping: w -= lr * clip(m / max(h, rho), 1)
    OmniResult compute_update(const double* momentum, double* output, uint32_t len, double lr) {
        if (len != num_params_) return {false, 0, "Length mismatch"};
        for (uint32_t i = 0; i < len; i++) {
            double h = std::max(hessian_diag_[i], rho_);
            double ratio = momentum[i] / h;
            double clipped = std::max(-1.0, std::min(1.0, ratio));
            output[i] = -lr * clipped;
        }
        return {true, lr, ""};
    }
};
