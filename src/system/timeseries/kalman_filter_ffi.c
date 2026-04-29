// OMNI SYSTEM LAYER: Time Series (C)
// FFI for ultra-fast 1D Kalman Filter state estimation.

#include <stdint.h>

extern "C" {

    // Simple 1D Kalman Filter
    struct KalmanState {
        double x; // State estimate
        double p; // Estimate error covariance
        double q; // Process noise covariance
        double r; // Measurement noise covariance
    };

    void omni_init_kalman(struct KalmanState* state, double initial_x, double initial_p, double q, double r) {
        if (!state) return;
        state->x = initial_x;
        state->p = initial_p;
        state->q = q;
        state->r = r;
    }

    // Process a batch of measurements, modifying measurements array in-place with filtered values
    int omni_kalman_filter_batch(struct KalmanState* state, double* measurements, int length) {
        if (!state || !measurements || length <= 0) return -1;

        for (int i = 0; i < length; i++) {
            // Prediction update
            state->p = state->p + state->q;

            // Measurement update
            double k = state->p / (state->p + state->r);
            state->x = state->x + k * (measurements[i] - state->x);
            state->p = (1.0 - k) * state->p;

            // Store filtered result back
            measurements[i] = state->x;
        }

        return 0; // Success
    }

}
