#include <vector>
#include <cmath>
#include <algorithm>
#include <stdexcept>

// OMNI System Layer: C++ Exact DBSCAN Implementation
// Optimized for contiguous memory layout, FFI ready.

extern "C" {

struct Point {
    float* coordinates;
    int cluster_id; // 0 = unclassified, -1 = noise
};

inline float euclidean_distance(const float* a, const float* b, int dimensions) {
    float sum = 0.0f;
    for (int i = 0; i < dimensions; ++i) {
        float diff = a[i] - b[i];
        sum += diff * diff;
    }
    return std::sqrt(sum);
}

void region_query(Point* points, int num_points, int target_idx, float eps, int dimensions, std::vector<int>& neighbors) {
    neighbors.clear();
    for (int i = 0; i < num_points; ++i) {
        if (euclidean_distance(points[target_idx].coordinates, points[i].coordinates, dimensions) <= eps) {
            neighbors.push_back(i);
        }
    }
}

bool expand_cluster(Point* points, int num_points, int point_idx, int cluster_id, float eps, int min_pts, int dimensions) {
    std::vector<int> seeds;
    region_query(points, num_points, point_idx, eps, dimensions, seeds);

    if (seeds.size() < static_cast<size_t>(min_pts)) {
        points[point_idx].cluster_id = -1; // Noise
        return false;
    } else {
        for (int i = 0; i < seeds.size(); ++i) {
            points[seeds[i]].cluster_id = cluster_id;
        }
        seeds.erase(std::remove(seeds.begin(), seeds.end(), point_idx), seeds.end());

        while (!seeds.empty()) {
            int current_p = seeds.front();
            std::vector<int> result;
            region_query(points, num_points, current_p, eps, dimensions, result);
            
            if (result.size() >= static_cast<size_t>(min_pts)) {
                for (int i = 0; i < result.size(); ++i) {
                    int result_p = result[i];
                    if (points[result_p].cluster_id == 0 || points[result_p].cluster_id == -1) {
                        if (points[result_p].cluster_id == 0) {
                            seeds.push_back(result_p);
                        }
                        points[result_p].cluster_id = cluster_id;
                    }
                }
            }
            seeds.erase(seeds.begin());
        }
        return true;
    }
}

// OMNI Entry point
int execute_dbscan(float* data_ptr, int num_points, int dimensions, float eps, int min_pts, int* out_labels) {
    std::vector<Point> dataset(num_points);
    for (int i = 0; i < num_points; ++i) {
        dataset[i].coordinates = &data_ptr[i * dimensions];
        dataset[i].cluster_id = 0;
    }

    int cluster_id = 1;
    for (int i = 0; i < num_points; ++i) {
        if (dataset[i].cluster_id == 0) {
            if (expand_cluster(dataset.data(), num_points, i, cluster_id, eps, min_pts, dimensions)) {
                cluster_id++;
            }
        }
    }

    for (int i = 0; i < num_points; ++i) {
        out_labels[i] = dataset[i].cluster_id;
    }
    return cluster_id - 1; // Total clusters
}

}
