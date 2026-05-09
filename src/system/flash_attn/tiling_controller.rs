/// @omni-layer System | @omni-source openai/triton | @omni-lang Rust
/// @omni-description Flash attention tiling controller: manages block iteration,
/// softmax accumulation, and output rescaling for memory-efficient attention.
#[derive(Debug)]
pub enum FlashError { InvalidBlockSize, EmptySequence }
pub type OmniResult<T> = Result<T, FlashError>;

pub struct TilingController { block_q: usize, block_kv: usize }

impl TilingController {
    pub fn new(block_q: usize, block_kv: usize) -> OmniResult<Self> {
        if block_q == 0 || block_kv == 0 { return Err(FlashError::InvalidBlockSize); }
        Ok(Self { block_q, block_kv })
    }
    pub fn compute_tile_schedule(&self, seq_len: usize) -> Vec<(usize, usize, usize, usize)> {
        let mut schedule = Vec::new();
        let mut qi = 0;
        while qi < seq_len {
            let qe = (qi + self.block_q).min(seq_len);
            let mut ki = 0;
            while ki < seq_len {
                let ke = (ki + self.block_kv).min(seq_len);
                schedule.push((qi, qe, ki, ke));
                ki = ke;
            }
            qi = qe;
        }
        schedule
    }
    pub fn estimate_memory(&self, seq_len: usize, d: usize) -> (usize, usize) {
        let standard = seq_len * seq_len * 4 + seq_len * d * 4;
        let flash = self.block_q * d * 4 + self.block_q * self.block_kv * 4 + self.block_q * 8;
        (standard, flash)
    }
    pub fn n_tiles(&self, seq_len: usize) -> usize {
        let q_tiles = (seq_len + self.block_q - 1) / self.block_q;
        let kv_tiles = (seq_len + self.block_kv - 1) / self.block_kv;
        q_tiles * kv_tiles
    }
}
