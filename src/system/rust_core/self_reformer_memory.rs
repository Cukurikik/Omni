pub struct SelfReformerMemory {
    pub size: usize,
}

impl SelfReformerMemory {
    pub fn new(size: usize) -> Self {
        SelfReformerMemory { size }
    }

    pub fn allocate(&self) -> Result<(), String> {
        if self.size == 0 {
            return Err("Invalid memory size".to_string());
        }
        Ok(())
    }
}
