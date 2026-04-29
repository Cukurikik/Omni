#include <vector>
#include <cmath>

namespace OmniReflect {
    double compute_joint_error(const std::vector<double>& target, const std::vector<double>& current) {
        double err = 0.0;
        for(size_t i=0; i<target.size(); ++i) {
            double diff = target[i] - current[i];
            err += diff * diff;
        }
        return std::sqrt(err);
    }
}
