// OMNI MOTHER: IBV Completion Queue
// Polls for RDMA work completions

pub struct OmniIbvCq {
    pub cqn: u32,
}

impl OmniIbvCq {
    pub fn new() -> Self {
        Self { cqn: 0 }
    }
    
    pub fn poll(&self) -> bool {
        true
    }
}
