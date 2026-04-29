#include <cstdint>

extern "C" {
    // OMNI System Layer - Gini Impurity for Decision Trees
    double compute_gini_impurity(const double* probabilities, int32_t len) {
        if (!probabilities || len <= 0) return 0.0;
        double sum_sq = 0.0;
        for(int32_t i=0; i<len; i++) {
            sum_sq += probabilities[i] * probabilities[i];
        }
        return 1.0 - sum_sq;
    }
}
