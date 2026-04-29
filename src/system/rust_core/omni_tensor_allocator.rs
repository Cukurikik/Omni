//! OmniTensorAllocator - Zero-Copy Memory Management
//!
//! Enforces zero-copy data transfer and strict memory safety 
//! for the OMNI System Layer using Rust's ownership model.

use std::alloc::{alloc, dealloc, Layout};
use std::ptr::NonNull;

/// Monadic error handling for system-level memory operations
#[derive(Debug)]
pub enum AllocError {
    LayoutError,
    OutOfMemory,
    InvalidPointer,
}

pub struct OmniTensorAllocator {
    ptr: NonNull<u8>,
    layout: Layout,
    capacity: usize,
}

impl OmniTensorAllocator {
    /// Allocate a zero-copy memory block for tensor data
    pub fn new(size_bytes: usize, align: usize) -> Result<Self, AllocError> {
        let layout = Layout::from_size_align(size_bytes, align)
            .map_err(|_| AllocError::LayoutError)?;

        let raw_ptr = unsafe { alloc(layout) };
        let ptr = NonNull::new(raw_ptr).ok_or(AllocError::OutOfMemory)?;

        Ok(OmniTensorAllocator {
            ptr,
            layout,
            capacity: size_bytes,
        })
    }

    /// Provide safe, zero-copy slice access to the memory
    pub fn as_slice(&self) -> &[u8] {
        unsafe { std::slice::from_raw_parts(self.ptr.as_ptr(), self.capacity) }
    }
    
    /// Provide safe, zero-copy mutable slice access
    pub fn as_mut_slice(&mut self) -> &mut [u8] {
        unsafe { std::slice::from_raw_parts_mut(self.ptr.as_ptr(), self.capacity) }
    }
}

impl Drop for OmniTensorAllocator {
    fn drop(&mut self) {
        unsafe {
            dealloc(self.ptr.as_ptr(), self.layout);
        }
    }
}
