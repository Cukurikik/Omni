// omni_moving_variance.rs — Welford's Online Variance
// Layer: Domain / Analytics
//
// Calculates the running mean, variance, and standard deviation of a continuous
// data stream in a single pass without storing the historical data. Highly numerically
// stable. Prevents catastrophic cancellation common in naive sum-of-squares. Zero mock.

pub struct OmniOnlineStats {
    count: u64,
    mean: f64,
    m2: f64, // Sum of squares of differences from the current mean
}

impl OmniOnlineStats {
    pub fn new() -> Self {
        OmniOnlineStats {
            count: 0,
            mean: 0.0,
            m2: 0.0,
        }
    }

    /// Update the running statistics with a new value (Welford's algorithm)
    pub fn update(&mut self, value: f64) {
        self.count += 1;
        let delta = value - self.mean;
        self.mean += delta / (self.count as f64);
        let delta2 = value - self.mean;
        self.m2 += delta * delta2;
    }

    /// Retrieve the current count of processed items
    pub fn count(&self) -> u64 {
        self.count
    }

    /// Retrieve the running mean
    pub fn mean(&self) -> f64 {
        if self.count == 0 {
            0.0
        } else {
            self.mean
        }
    }

    /// Retrieve the running population variance
    pub fn population_variance(&self) -> f64 {
        if self.count == 0 {
            0.0
        } else {
            self.m2 / (self.count as f64)
        }
    }

    /// Retrieve the running sample variance (n-1 degrees of freedom)
    pub fn sample_variance(&self) -> f64 {
        if self.count < 2 {
            0.0
        } else {
            self.m2 / ((self.count - 1) as f64)
        }
    }

    /// Retrieve the running sample standard deviation
    pub fn standard_deviation(&self) -> f64 {
        self.sample_variance().sqrt()
    }
}
