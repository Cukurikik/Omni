// omni_kalman_1d.rs — 1D Kalman Filter
// Layer: Domain / Analytics
//
// Implements a discrete linear 1D Kalman Filter. Optimal for smoothing
// noisy sensor data (e.g., IoT temperature readings, GPS jitter) by balancing
// predicted system state against actual noisy measurements. Zero mock.

pub struct OmniKalman1D {
    state: f64,              // Estimated state (x)
    covariance: f64,         // Error covariance (P)
    process_noise: f64,      // Process noise variance (Q) - model confidence
    measurement_noise: f64,  // Measurement noise variance (R) - sensor confidence
}

impl OmniKalman1D {
    /// Initializes a new 1D Kalman Filter.
    /// `initial_state`: First guess of the value.
    /// `initial_covariance`: High if the initial state is a wild guess.
    /// `process_noise`: Small value (>0), defines how much the true state can jump between steps.
    /// `measurement_noise`: Variance of the sensor noise.
    pub fn new(initial_state: f64, initial_covariance: f64, process_noise: f64, measurement_noise: f64) -> Self {
        OmniKalman1D {
            state: initial_state,
            covariance: initial_covariance,
            process_noise,
            measurement_noise,
        }
    }

    /// Process a new measurement and update the internal state
    pub fn update(&mut self, measurement: f64) -> f64 {
        // --- Prediction Step ---
        // 1. Project the state ahead (Since it's 1D and assuming constant model, state = state)
        let predicted_state = self.state;
        
        // 2. Project the error covariance ahead
        let predicted_covariance = self.covariance + self.process_noise;

        // --- Update Step ---
        // 1. Compute Kalman Gain
        // K = P_pred / (P_pred + R)
        let kalman_gain = predicted_covariance / (predicted_covariance + self.measurement_noise);

        // 2. Update estimate with measurement
        // x = x_pred + K * (z - x_pred)
        self.state = predicted_state + kalman_gain * (measurement - predicted_state);

        // 3. Update error covariance
        // P = (1 - K) * P_pred
        self.covariance = (1.0 - kalman_gain) * predicted_covariance;

        self.state
    }

    /// Return the current best estimate of the state
    pub fn get_state(&self) -> f64 {
        self.state
    }

    /// Return the current uncertainty (covariance)
    pub fn get_covariance(&self) -> f64 {
        self.covariance
    }
}
