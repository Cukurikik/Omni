/// @omni-layer System | @omni-source microsoft/DeepSpeed | @omni-lang Rust
/// @omni-description Expert capacity buffer: memory pool for MoE token routing
/// with capacity tracking and overflow handling.
#[derive(Debug)]
pub enum MoEError { CapacityExceeded, InvalidExpert(usize) }
pub type OmniResult<T> = Result<T, MoEError>;

pub struct ExpertBuffer {
    n_experts: usize, capacity: usize, d: usize,
    buffers: Vec<Vec<Vec<f64>>>,
    counts: Vec<usize>,
    overflow: Vec<(usize, Vec<f64>)>,
}
impl ExpertBuffer {
    pub fn new(n_experts: usize, capacity: usize, d: usize) -> Self {
        Self {
            n_experts, capacity, d,
            buffers: (0..n_experts).map(|_| Vec::with_capacity(capacity)).collect(),
            counts: vec![0; n_experts], overflow: Vec::new(),
        }
    }
    pub fn route_token(&mut self, expert_id: usize, token: Vec<f64>) -> OmniResult<bool> {
        if expert_id >= self.n_experts { return Err(MoEError::InvalidExpert(expert_id)); }
        if self.counts[expert_id] >= self.capacity {
            self.overflow.push((expert_id, token));
            return Ok(false);
        }
        self.buffers[expert_id].push(token);
        self.counts[expert_id] += 1;
        Ok(true)
    }
    pub fn get_expert_batch(&self, expert_id: usize) -> OmniResult<&[Vec<f64>]> {
        if expert_id >= self.n_experts { return Err(MoEError::InvalidExpert(expert_id)); }
        Ok(&self.buffers[expert_id])
    }
    pub fn utilization(&self) -> Vec<f64> {
        self.counts.iter().map(|&c| c as f64 / self.capacity as f64).collect()
    }
    pub fn total_overflow(&self) -> usize { self.overflow.len() }
    pub fn reset(&mut self) {
        for buf in &mut self.buffers { buf.clear(); }
        self.counts = vec![0; self.n_experts];
        self.overflow.clear();
    }
}
