#include <cstdint>
#include <cmath>

extern "C" {
    // OMNI System Layer - BPR Loss Function for Recommendation Tuning
    double compute_bpr_loss(const double* pos_scores, const double* neg_scores, int32_t length) {
        if (!pos_scores || !neg_scores || length <= 0) return 0.0;
        
        double loss = 0.0;
        for (int32_t i = 0; i < length; ++i) {
            double diff = pos_scores[i] - neg_scores[i];
            // log(sigmoid(x))
            loss -= std::log(1.0 / (1.0 + std::exp(-diff)));
        }
        return loss / length;
    }
}
