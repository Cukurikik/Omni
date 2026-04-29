#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// OMNI PATTERN CLASSIFICATION: k-NN (C implementation, GPU logic simulacrum)
// Euclidean distance based K-Nearest Neighbors core.
// Source: rasbt/pattern_classification

typedef struct {
    float* features;
    int label;
} DataPoint;

typedef struct {
    float distance;
    int label;
} DistLabel;

typedef enum {
    KNN_SUCCESS = 0,
    KNN_ERR_INVALID_K = 1,
    KNN_ERR_NULL_PTR = 2
} KnnError;

// Computes squared Euclidean distance
float squared_euclidean(float* a, float* b, int dims) {
    float dist = 0.0f;
    for (int i = 0; i < dims; ++i) {
        float diff = a[i] - b[i];
        dist += diff * diff;
    }
    return dist;
}

// Simple selection sort for finding top-k smallest distances
void sort_k_smallest(DistLabel* arr, int n, int k) {
    for (int i = 0; i < k && i < n; ++i) {
        int min_idx = i;
        for (int j = i + 1; j < n; ++j) {
            if (arr[j].distance < arr[min_idx].distance) {
                min_idx = j;
            }
        }
        // Swap
        DistLabel temp = arr[i];
        arr[i] = arr[min_idx];
        arr[min_idx] = temp;
    }
}

// Core KNN Predict
KnnError knn_predict(DataPoint* train_data, int num_train, int dims, int k, float* query, int num_classes, int* out_label) {
    if (!train_data || !query || !out_label) return KNN_ERR_NULL_PTR;
    if (k <= 0 || k > num_train) return KNN_ERR_INVALID_K;

    // Allocate distance array
    DistLabel* distances = (DistLabel*)malloc(num_train * sizeof(DistLabel));
    if (!distances) return KNN_ERR_NULL_PTR;

    // Compute distances
    for (int i = 0; i < num_train; ++i) {
        distances[i].distance = squared_euclidean(train_data[i].features, query, dims);
        distances[i].label = train_data[i].label;
    }

    // Find K nearest
    sort_k_smallest(distances, num_train, k);

    // Majority voting
    int* class_counts = (int*)calloc(num_classes, sizeof(int));
    for (int i = 0; i < k; ++i) {
        class_counts[distances[i].label]++;
    }

    int best_class = 0;
    int max_votes = -1;
    for (int c = 0; c < num_classes; ++c) {
        if (class_counts[c] > max_votes) {
            max_votes = class_counts[c];
            best_class = c;
        }
    }

    *out_label = best_class;

    free(class_counts);
    free(distances);

    return KNN_SUCCESS;
}
