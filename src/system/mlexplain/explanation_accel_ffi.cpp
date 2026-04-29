#include <vector>
#include <cmath>

extern "C" {

    struct OmniAccelResult {
        double* distances;
        int size;
        const char* error;
    };

    void omni_free_accel_result(OmniAccelResult* res) {
        if (res) {
            if (res->distances) delete[] res->distances;
            // error strings are static or strdup-ed
            delete res;
        }
    }

    // High-performance pairwise L2 distance acceleration for Trust Score computation
    OmniAccelResult* compute_pairwise_l2(const double* query, const double* dataset, int num_samples, int features) {
        OmniAccelResult* result = new OmniAccelResult{nullptr, 0, nullptr};

        if (!query || !dataset || num_samples <= 0 || features <= 0) {
            result->error = "Invalid matrix parameters for pairwise L2";
            return result;
        }

        result->distances = new double[num_samples];
        result->size = num_samples;

        // Loop unrolling for SIMD vectorization potential
        for (int i = 0; i < num_samples; ++i) {
            double sum_sq = 0.0;
            const double* current_sample = &dataset[i * features];
            
            for (int j = 0; j < features; ++j) {
                double diff = query[j] - current_sample[j];
                sum_sq += diff * diff;
            }
            result->distances[i] = std::sqrt(sum_sq);
        }

        return result;
    }
}
