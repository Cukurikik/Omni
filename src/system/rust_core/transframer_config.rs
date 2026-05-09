pub struct TransframerConfig {
    pub depth: usize,
}

impl TransframerConfig {
    pub fn new() -> Self {
        TransframerConfig { depth: 6 }
    }
}
