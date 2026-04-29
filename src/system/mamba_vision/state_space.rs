use omni_std::result::{Result, Ok, Err};

pub struct StateSpace {
    dim: usize,
}

impl StateSpace {
    pub fn new(dim: usize) -> Result<Self, String> {
        if dim == 0 { return Err("Dimension must be > 0".to_string()); }
        Ok(StateSpace { dim })
    }
}
