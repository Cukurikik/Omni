#include <cstdint>

extern "C" {
    // OMNI System Layer - High-precision F1 scoring kernel
    double compute_f1_score(double true_positive, double false_positive, double false_negative) {
        if (true_positive <= 0.0) return 0.0;
        
        double precision = true_positive / (true_positive + false_positive);
        double recall = true_positive / (true_positive + false_negative);
        
        if (precision + recall == 0.0) return 0.0;
        
        return 2.0 * (precision * recall) / (precision + recall);
    }
}
