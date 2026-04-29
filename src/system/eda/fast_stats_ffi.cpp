#include <vector>
#include <algorithm>
#include <cmath>
#include <iostream>

enum class OmniStatus {
    OK = 0,
    NULL_POINTER = 1,
    EMPTY_ARRAY = 2
};

struct OmniStatsResult {
    OmniStatus status;
    double min;
    double max;
    double mean;
    double variance;
    double median;
};

extern "C" {

    // Computes comprehensive statistics for a single column incredibly fast
    OmniStatsResult compute_fast_stats(const double* data, size_t length) {
        if (!data) return {OmniStatus::NULL_POINTER, 0, 0, 0, 0, 0};
        if (length == 0) return {OmniStatus::EMPTY_ARRAY, 0, 0, 0, 0, 0};

        std::vector<double> vec(data, data + length);
        
        double sum = 0.0;
        double min_val = vec[0];
        double max_val = vec[0];

        // First pass for mean, min, max
        for (size_t i = 0; i < length; ++i) {
            double val = vec[i];
            sum += val;
            if (val < min_val) min_val = val;
            if (val > max_val) max_val = val;
        }

        double mean = sum / length;

        // Second pass for variance
        double sq_sum = 0.0;
        for (size_t i = 0; i < length; ++i) {
            double diff = vec[i] - mean;
            sq_sum += diff * diff;
        }
        double variance = sq_sum / length;

        // Median requires partial sorting (O(N) on average)
        size_t n = length / 2;
        std::nth_element(vec.begin(), vec.begin() + n, vec.end());
        double median = vec[n];

        if (length % 2 == 0) {
            auto max_it = std::max_element(vec.begin(), vec.begin() + n);
            median = (*max_it + median) / 2.0;
        }

        return {OmniStatus::OK, min_val, max_val, mean, variance, median};
    }
}
