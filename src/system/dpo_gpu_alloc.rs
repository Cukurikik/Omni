// OMNI System Layer - DPO GPU Allocator
pub enum VRAMError {
    OutOfMemory,
    DeviceOffline,
}

pub struct GPUAllocator {
    pub total_memory: usize,
    pub used_memory: usize,
}

impl GPUAllocator {
    pub fn allocate_batch(&mut self, batch_size: usize) -> Result<usize, VRAMError> {
        let required = batch_size * 1024 * 1024; // approx 1MB per item
        if self.used_memory + required > self.total_memory {
            return Err(VRAMError::OutOfMemory);
        }
        
        self.used_memory += required;
        Ok(self.used_memory)
    }
}
