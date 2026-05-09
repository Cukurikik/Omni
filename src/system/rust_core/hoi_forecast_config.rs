pub struct HoiForecastConfig {
    pub seq_length: usize,
}

impl HoiForecastConfig {
    pub fn new() -> Self {
        HoiForecastConfig { seq_length: 16 }
    }
}
