#include <cstdint>
#include <cmath>

extern "C" {
    // Fast cosine similarity kernel for LLMs4OL ontology alignment
    float llms4ol_fast_cosine_similarity(const float* vec_a, const float* vec_b, uint32_t dim) {
        float dot = 0.0f;
        float norm_a = 0.0f;
        float norm_b = 0.0f;
        
        for (uint32_t i = 0; i < dim; ++i) {
            dot += vec_a[i] * vec_b[i];
            norm_a += vec_a[i] * vec_a[i];
            norm_b += vec_b[i] * vec_b[i];
        }
        
        float denom = std::sqrt(norm_a) * std::sqrt(norm_b);
        if (denom < 1e-8f) return 0.0f;
        return dot / denom;
    }
}
