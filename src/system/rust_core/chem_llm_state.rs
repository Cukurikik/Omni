pub struct ChemLLMState {
    pub is_loaded: bool,
}

impl ChemLLMState {
    pub fn new() -> Self {
        ChemLLMState { is_loaded: false }
    }
}
