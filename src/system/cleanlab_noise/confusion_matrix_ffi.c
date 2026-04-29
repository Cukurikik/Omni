#include <stdint.h>
#include <stdlib.h>

extern "C" {

// Fast Joint Error Confusion Matrix population FFI for cleanlab
void omni_compute_confusion_matrix(
    const int32_t* given_labels,
    const int32_t* predicted_labels,
    int32_t num_samples,
    int32_t num_classes,
    int32_t* out_matrix, // pre-allocated num_classes * num_classes
    int32_t* err_code
) {
    if (!err_code) return;

    if (!given_labels || !predicted_labels || !out_matrix) {
        *err_code = -1;
        return;
    }

    if (num_samples <= 0 || num_classes <= 0) {
        *err_code = -2;
        return;
    }

    // Zero out the matrix
    for (int32_t i = 0; i < num_classes * num_classes; ++i) {
        out_matrix[i] = 0;
    }

    // Deterministic tight loop for fast counting
    for (int32_t i = 0; i < num_samples; ++i) {
        int32_t given = given_labels[i];
        int32_t pred = predicted_labels[i];

        if (given < 0 || given >= num_classes || pred < 0 || pred >= num_classes) {
            *err_code = -3; // Out of bounds class
            return;
        }

        int32_t idx = given * num_classes + pred;
        out_matrix[idx] += 1;
    }

    *err_code = 0;
}

}
