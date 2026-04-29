#include <vector>
#include <cmath>
#include <algorithm>
#include <stdexcept>

namespace omni::mlpack {

struct Neighbor {
    size_t index;
    double distance;
    bool operator<(const Neighbor& other) const {
        return distance < other.distance;
    }
};

class KNN {
public:
    KNN(size_t k) : k_(k) {}

    // OMNI Engine: Exact K-Nearest Neighbors using optimized linear scan
    // In production, this would bridge to kd-tree or ball-tree
    std::vector<std::vector<Neighbor>> search(
        const std::vector<std::vector<double>>& reference_set,
        const std::vector<std::vector<double>>& query_set) const {
        
        if (reference_set.empty() || query_set.empty()) {
            throw std::invalid_argument("Empty sets provided to KNN.");
        }

        std::vector<std::vector<Neighbor>> results(query_set.size());

        for (size_t q = 0; q < query_set.size(); ++q) {
            std::vector<Neighbor> neighbors;
            neighbors.reserve(reference_set.size());

            for (size_t r = 0; r < reference_set.size(); ++r) {
                double dist = euclidean_distance(query_set[q], reference_set[r]);
                neighbors.push_back({r, dist});
            }

            // Partially sort to get top k
            std::partial_sort(neighbors.begin(), neighbors.begin() + k_, neighbors.end());
            neighbors.resize(k_);
            results[q] = std::move(neighbors);
        }

        return results;
    }

private:
    size_t k_;

    double euclidean_distance(const std::vector<double>& a, const std::vector<double>& b) const {
        double sum = 0.0;
        for (size_t i = 0; i < a.size(); ++i) {
            double diff = a[i] - b[i];
            sum += diff * diff;
        }
        return std::sqrt(sum);
    }
};

} // namespace omni::mlpack
