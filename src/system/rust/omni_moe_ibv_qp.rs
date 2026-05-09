// OMNI MOTHER: IBV Queue Pair
// Manages RDMA Send/Recv Queues

pub struct OmniIbvQp {
    pub qpn: u32,
}

impl OmniIbvQp {
    pub fn new() -> Self {
        Self { qpn: 0 }
    }
}
