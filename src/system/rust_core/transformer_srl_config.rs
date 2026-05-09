pub struct TransformerSRLConfig {
    pub num_labels: usize,
}

impl TransformerSRLConfig {
    pub fn new() -> Self {
        TransformerSRLConfig { num_labels: 104 }
    }
}
