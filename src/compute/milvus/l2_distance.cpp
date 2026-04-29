#include <vector>
#include <stdexcept>
#include <cmath>

// OMNI MILVUS: L2 Distance (Squared Euclidean) Computation
// Core math for vector similarity search. In production, this utilizes AVX-512 intrinsics.
// Source: milvus-io/milvus

namespace omni::milvus {

enum class DistanceError {
    SUCCESS,
    DIMENSION_MISMATCH,
    NULL_POINTER
};

template<typename T>
struct Result {
    T value;
    DistanceError error;
    bool is_ok() const { return error == DistanceError::SUCCESS; }
};

class VectorMath {
public:
    /**
     * Computes the squared L2 distance between two vectors.
     * Squared distance is used because it preserves ordering and avoids the expensive sqrt() call
     * during the massive number of comparisons in HNSW/IVF index traversals.
     */
    static Result<float> compute_l2_sqr(const float* vec_a, const float* vec_b, size_t dim) {
        if (!vec_a || !vec_b) {
            return {0.0f, DistanceError::NULL_POINTER};
        }

        float dist_sq = 0.0f;
        
        // Simulated auto-vectorization loop (compiler will unroll and use SIMD if aligned)
        // #pragma omp simd // Uncomment for OpenMP SIMD
        for (size_t i = 0; i < dim; ++i) {
            float diff = vec_a[i] - vec_b[i];
            dist_sq += diff * diff;
        }

        return {dist_sq, DistanceError::SUCCESS};
    }

    /**
     * Computes Cosine Similarity.
     * Requires dot product and magnitudes.
     */
    static Result<float> compute_cosine(const float* vec_a, const float* vec_b, size_t dim) {
        if (!vec_a || !vec_b) {
            return {0.0f, DistanceError::NULL_POINTER};
        }

        float dot = 0.0f;
        float norm_a_sq = 0.0f;
        float norm_b_sq = 0.0f;

        for (size_t i = 0; i < dim; ++i) {
            dot += vec_a[i] * vec_b[i];
            norm_a_sq += vec_a[i] * vec_a[i];
            norm_b_sq += vec_b[i] * vec_b[i];
        }

        if (norm_a_sq == 0.0f || norm_b_sq == 0.0f) {
            return {0.0f, DistanceError::SUCCESS}; // Handle zero-vectors
        }

        float similarity = dot / (std::sqrt(norm_a_sq) * std::sqrt(norm_b_sq));
        return {similarity, DistanceError::SUCCESS};
    }
};

} // namespace omni::milvus
