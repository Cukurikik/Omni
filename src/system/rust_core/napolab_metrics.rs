pub struct NapolabMetrics {
    pub current_accuracy: f32,
}

impl NapolabMetrics {
    pub fn new() -> Self {
        NapolabMetrics { current_accuracy: 0.0 }
    }
}
