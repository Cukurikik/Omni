// OMNI Framework - Rust Memory Management for GHN3 Hypernetworks
// Ensures zero-copy memory mapping for large hypernetwork parameter transfers.

use std::alloc::{alloc, dealloc, Layout};
use std::ptr::NonNull;

pub struct OmniHypernetworkMemory {
    ptr: NonNull<u8>,
    layout: Layout,
    size: usize,
}

impl OmniHypernetworkMemory {
    pub fn new(size: usize) -> Result<Self, &'static str> {
        let layout = Layout::array::<u8>(size).map_err(|_| "Layout error")?;
        let ptr = unsafe { alloc(layout) };
        let ptr = NonNull::new(ptr).ok_or("Allocation failed")?;
        Ok(Self { ptr, layout, size })
    }

    pub fn get_slice_mut(&mut self) -> &mut [u8] {
        unsafe { std::slice::from_raw_parts_mut(self.ptr.as_ptr(), self.size) }
    }

    pub fn get_slice(&self) -> &[u8] {
        unsafe { std::slice::from_raw_parts(self.ptr.as_ptr(), self.size) }
    }
}

impl Drop for OmniHypernetworkMemory {
    fn drop(&mut self) {
        unsafe {
            dealloc(self.ptr.as_ptr(), self.layout);
        }
    }
}
