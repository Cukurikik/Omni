#include <vector>
#include <cmath>
#include <algorithm>

namespace ssl {

double contrastive_loss(const std::vector<double>& z_i, const std::vector<double>& z_j, double temperature) {
    double dot_product = 0.0;
    double norm_i = 0.0;
    double norm_j = 0.0;
    
    for (size_t i = 0; i < z_i.size(); ++i) {
        dot_product += z_i[i] * z_j[i];
        norm_i += z_i[i] * z_i[i];
        norm_j += z_j[i] * z_j[i];
    }
    
    double sim = dot_product / (std::sqrt(norm_i) * std::sqrt(norm_j));
    // Simplified InfoNCE loss component
    return -std::log(std::exp(sim / temperature));
}

} // namespace ssl
