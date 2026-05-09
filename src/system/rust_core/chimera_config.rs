pub struct ChimeraConfig {
    pub num_stages: usize,
}

impl ChimeraConfig {
    pub fn new() -> Self {
        ChimeraConfig { num_stages: 4 }
    }
}
