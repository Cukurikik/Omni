pub struct FluenceState {
    pub is_robust: bool,
}

impl FluenceState {
    pub fn new() -> Self {
        FluenceState { is_robust: true }
    }
}
