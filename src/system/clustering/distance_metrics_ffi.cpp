#include <cmath>
#include <vector>
#include <iostream>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Omni FFI Status Code
enum class OmniStatus {
    OK = 0,
    NULL_POINTER = 1,
    INVALID_DIMENSIONS = 2,
    COMPUTATION_ERROR = 3
};

struct OmniResult {
    OmniStatus status;
    double* data;
    size_t length;
};

extern "C" {

    // Computes pairwise Euclidean distance matrix
    // Caller is responsible for freeing the returned data array via omni_free
    OmniResult compute_pairwise_euclidean(const double* data, size_t n_samples, size_t n_features) {
        if (!data) {
            return {OmniStatus::NULL_POINTER, nullptr, 0};
        }
        if (n_samples == 0 || n_features == 0) {
            return {OmniStatus::INVALID_DIMENSIONS, nullptr, 0};
        }

        size_t matrix_size = n_samples * n_samples;
        double* dist_matrix = new(std::nothrow) double[matrix_size];
        
        if (!dist_matrix) {
            return {OmniStatus::COMPUTATION_ERROR, nullptr, 0};
        }

        for (size_t i = 0; i < n_samples; ++i) {
            for (size_t j = i; j < n_samples; ++j) {
                if (i == j) {
                    dist_matrix[i * n_samples + j] = 0.0;
                } else {
                    double sum_sq = 0.0;
                    for (size_t k = 0; k < n_features; ++k) {
                        double diff = data[i * n_features + k] - data[j * n_features + k];
                        sum_sq += diff * diff;
                    }
                    double dist = std::sqrt(sum_sq);
                    dist_matrix[i * n_samples + j] = dist;
                    dist_matrix[j * n_samples + i] = dist; // Symmetric
                }
            }
        }

        return {OmniStatus::OK, dist_matrix, matrix_size};
    }

    // Computes pairwise Haversine distance matrix for geo data
    OmniResult compute_pairwise_haversine(const double* lat_lon_data, size_t n_samples) {
        if (!lat_lon_data) {
            return {OmniStatus::NULL_POINTER, nullptr, 0};
        }
        if (n_samples == 0) {
            return {OmniStatus::INVALID_DIMENSIONS, nullptr, 0};
        }

        size_t matrix_size = n_samples * n_samples;
        double* dist_matrix = new(std::nothrow) double[matrix_size];
        
        if (!dist_matrix) {
            return {OmniStatus::COMPUTATION_ERROR, nullptr, 0};
        }

        const double R = 6371000.0; // Earth radius in meters

        for (size_t i = 0; i < n_samples; ++i) {
            for (size_t j = i; j < n_samples; ++j) {
                if (i == j) {
                    dist_matrix[i * n_samples + j] = 0.0;
                } else {
                    double lat1 = lat_lon_data[i * 2] * M_PI / 180.0;
                    double lon1 = lat_lon_data[i * 2 + 1] * M_PI / 180.0;
                    double lat2 = lat_lon_data[j * 2] * M_PI / 180.0;
                    double lon2 = lat_lon_data[j * 2 + 1] * M_PI / 180.0;

                    double dlat = lat2 - lat1;
                    double dlon = lon2 - lon1;

                    double a = std::sin(dlat / 2.0) * std::sin(dlat / 2.0) +
                               std::cos(lat1) * std::cos(lat2) *
                               std::sin(dlon / 2.0) * std::sin(dlon / 2.0);
                    
                    double c = 2.0 * std::atan2(std::sqrt(a), std::sqrt(1.0 - a));
                    double dist = R * c;

                    dist_matrix[i * n_samples + j] = dist;
                    dist_matrix[j * n_samples + i] = dist;
                }
            }
        }

        return {OmniStatus::OK, dist_matrix, matrix_size};
    }

    void omni_free_dist_matrix(double* ptr) {
        if (ptr) {
            delete[] ptr;
        }
    }
}
