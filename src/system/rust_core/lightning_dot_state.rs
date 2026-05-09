pub struct LightningDOTState {
    pub is_indexed: bool,
}

impl LightningDOTState {
    pub fn new() -> Self {
        LightningDOTState { is_indexed: false }
    }
}
