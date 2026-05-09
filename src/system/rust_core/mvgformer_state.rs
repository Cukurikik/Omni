pub struct MVGFormerState {
    pub num_views_active: usize,
}

impl MVGFormerState {
    pub fn new() -> Self {
        MVGFormerState { num_views_active: 0 }
    }
}
