// OMNI System Layer - LlamaFactory GPU Alloc
pub enum VRAMError {
    InsufficientMemory,
}

pub struct GPUAllocator {
    pub available_mb: usize,
}

impl GPUAllocator {
    pub fn allocate_peft_adapters(&mut self, rank: usize, layers: usize) -> Result<usize, VRAMError> {
        let required_mb = rank * layers * 2; // Approximation for 16-bit precision
        if self.available_mb < required_mb {
            return Err(VRAMError::InsufficientMemory);
        }
        
        self.available_mb -= required_mb;
        Ok(required_mb)
    }
}
