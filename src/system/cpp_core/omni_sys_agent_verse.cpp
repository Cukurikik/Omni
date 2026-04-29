#include <cstdint>
#include <cmath>

// OMNI System Kernel: Bipartite matching score
extern "C" {
        double compute(const double* affinity_matrix, int32_t rows, int32_t cols) {
            double score = 0.0;
            for(int i=0; i<rows && i<cols; i++) score += affinity_matrix[i * cols + i];
            return score;
        }
}