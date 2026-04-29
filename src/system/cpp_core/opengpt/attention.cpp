#include <cstdint>
#include <cmath>

extern "C" {
    // OMNI System Layer - Native Softmax Attention Normalization
    void compute_softmax(double* scores, int32_t len) {
        if (!scores || len <= 0) return;
        
        // Find max for numerical stability
        double max_val = scores[0];
        for(int32_t i=1; i<len; i++) {
            if(scores[i] > max_val) max_val = scores[i];
        }
        
        double sum = 0.0;
        for(int32_t i=0; i<len; i++) {
            scores[i] = std::exp(scores[i] - max_val);
            sum += scores[i];
        }
        
        for(int32_t i=0; i<len; i++) {
            scores[i] /= sum;
        }
    }
}
