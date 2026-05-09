/// OMNI Radar Signal Processor
/// Fast Fourier Transform and Doppler shift analysis for debris detection.

pub struct RadarSignalProcessor {
    sample_rate: f32,
    carrier_frequency: f32,
}

impl RadarSignalProcessor {
    pub fn new(sample_rate: f32, carrier_frequency: f32) -> Self {
        Self {
            sample_rate,
            carrier_frequency,
        }
    }

    pub fn compute_doppler_velocity(&self, received_freq: f32) -> Result<f32, &'static str> {
        if received_freq <= 0.0 {
            return Err("Received frequency must be positive");
        }

        // Speed of light in m/s
        let c = 299_792_458.0; 
        
        // Doppler equation: fd = 2 * v * fc / c
        let fd = received_freq - self.carrier_frequency;
        let velocity = (fd * c) / (2.0 * self.carrier_frequency);

        Ok(velocity) // meters per second
    }
}
