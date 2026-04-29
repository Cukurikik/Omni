// OMNI System Layer - Lexoid Memory
use std::alloc::{alloc, dealloc, Layout};
use std::ptr;

pub enum LexoidMemError {
    AllocationFailed,
    InvalidLayout,
}

pub struct MemoryRegion {
    ptr: *mut u8,
    layout: Layout,
}

impl MemoryRegion {
    pub fn new(size: usize, align: usize) -> Result<Self, LexoidMemError> {
        let layout = Layout::from_size_align(size, align)
            .map_err(|_| LexoidMemError::InvalidLayout)?;
            
        let ptr = unsafe { alloc(layout) };
        if ptr.is_null() {
            return Err(LexoidMemError::AllocationFailed);
        }
        
        Ok(Self { ptr, layout })
    }
}

impl Drop for MemoryRegion {
    fn drop(&mut self) {
        unsafe {
            dealloc(self.ptr, self.layout);
        }
    }
}
