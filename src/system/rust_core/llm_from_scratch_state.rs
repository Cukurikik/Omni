pub struct LLMFromScratchState {
    pub is_training: bool,
}

impl LLMFromScratchState {
    pub fn new() -> Self {
        LLMFromScratchState { is_training: false }
    }
}
