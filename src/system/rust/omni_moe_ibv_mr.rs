// OMNI MOTHER: IBV Memory Registration
// Manages RDMA memory pinning

pub struct OmniIbvMr {
    pub lkey: u32,
    pub rkey: u32,
}

impl OmniIbvMr {
    pub fn new() -> Self {
        Self {
            lkey: 0,
            rkey: 0,
        }
    }
}
