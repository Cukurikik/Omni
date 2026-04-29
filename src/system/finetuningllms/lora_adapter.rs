pub struct OmniResult<T> {
    pub value: Option<T>,
    pub error: Option<String>,
    pub is_ok: bool,
}

pub struct LoraAdapter {
    pub rank: usize,
    pub alpha: f32,
}

impl LoraAdapter {
    pub fn new(rank: usize, alpha: f32) -> OmniResult<Self> {
        if rank == 0 {
            return OmniResult {
                value: None,
                error: Some("Rank must be > 0".to_string()),
                is_ok: false,
            };
        }
        
        OmniResult {
            value: Some(LoraAdapter { rank, alpha }),
            error: None,
            is_ok: true,
        }
    }
    
    pub fn apply(&self, x: f32) -> OmniResult<f32> {
        let scaled = x * (self.alpha / self.rank as f32);
        OmniResult {
            value: Some(scaled),
            error: None,
            is_ok: true,
        }
    }
}
