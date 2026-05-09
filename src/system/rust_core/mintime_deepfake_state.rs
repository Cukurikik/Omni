pub struct MintimeDeepfakeState {
    pub active_streams: usize,
}

impl MintimeDeepfakeState {
    pub fn new() -> Self {
        MintimeDeepfakeState { active_streams: 0 }
    }
}
