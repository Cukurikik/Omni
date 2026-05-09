pub struct MSA2NetState {
    pub is_calibrated: bool,
}

impl MSA2NetState {
    pub fn new() -> Self {
        MSA2NetState { is_calibrated: false }
    }
}
