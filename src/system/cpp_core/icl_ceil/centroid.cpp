#include <cstdint>
#include <vector>

extern "C" {
    // OMNI System Layer - SIMD-ready centroid updates
    void compute_new_centroids(const double* data, const int32_t* labels, double* out_centroids, 
                               int32_t num_points, int32_t dim, int32_t k) {
        if (!data || !labels || !out_centroids) return;
        
        std::vector<int32_t> counts(k, 0);
        
        for (int32_t i = 0; i < num_points; ++i) {
            int32_t cluster = labels[i];
            if (cluster >= 0 && cluster < k) {
                counts[cluster]++;
                for (int32_t d = 0; d < dim; ++d) {
                    out_centroids[cluster * dim + d] += data[i * dim + d];
                }
            }
        }
        
        for (int32_t i = 0; i < k; ++i) {
            if (counts[i] > 0) {
                for (int32_t d = 0; d < dim; ++d) {
                    out_centroids[i * dim + d] /= counts[i];
                }
            }
        }
    }
}
