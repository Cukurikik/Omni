#include <cstdint>
#include <algorithm>
#include <vector>

extern "C" {
    // OMNI System Layer - Greedy bipartite matching approximation kernel
    double compute_bipartite_score(const double* weights, int32_t rows, int32_t cols) {
        if (!weights || rows <= 0 || cols <= 0) return 0.0;
        
        std::vector<double> w(weights, weights + (rows * cols));
        double score = 0.0;
        int32_t limit = std::min(rows, cols);
        
        for (int32_t k = 0; k < limit; ++k) {
            double max_val = 0.0;
            int32_t max_r = -1, max_c = -1;
            
            for (int32_t r = 0; r < rows; ++r) {
                for (int32_t c = 0; c < cols; ++c) {
                    double val = w[r * cols + c];
                    if (val > max_val) {
                        max_val = val;
                        max_r = r;
                        max_c = c;
                    }
                }
            }
            
            if (max_val <= 0.0) break;
            
            score += max_val;
            for (int32_t c = 0; c < cols; ++c) w[max_r * cols + c] = 0.0;
            for (int32_t r = 0; r < rows; ++r) w[r * cols + max_c] = 0.0;
        }
        
        return score;
    }
}
