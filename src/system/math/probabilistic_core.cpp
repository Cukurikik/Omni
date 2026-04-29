#include <cmath>
#include <vector>
#include <stdexcept>

namespace OmniProbML {

class GaussianDistribution {
private:
    double mu;
    double sigma;

public:
    GaussianDistribution(double mean, double stddev) : mu(mean), sigma(stddev) {
        if (sigma <= 0) throw std::invalid_argument("Sigma must be > 0");
    }

    double pdf(double x) const {
        const double inv_sqrt_2pi = 0.3989422804014327;
        double a = (x - mu) / sigma;
        return (inv_sqrt_2pi / sigma) * std::exp(-0.5f * a * a);
    }

    double log_pdf(double x) const {
        const double log_inv_sqrt_2pi = -0.9189385332046727;
        double a = (x - mu) / sigma;
        return log_inv_sqrt_2pi - std::log(sigma) - 0.5f * a * a;
    }
};

}
