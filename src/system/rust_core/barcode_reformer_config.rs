pub struct BarCodeReformerConfig {
    pub hidden_dim: usize,
}

impl BarCodeReformerConfig {
    pub fn new() -> Self {
        BarCodeReformerConfig { hidden_dim: 256 }
    }
}
