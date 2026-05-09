pub struct CybertronMindsporeConfig {
    pub hidden_size: usize,
}

impl CybertronMindsporeConfig {
    pub fn new() -> Self {
        CybertronMindsporeConfig { hidden_size: 768 }
    }
}
