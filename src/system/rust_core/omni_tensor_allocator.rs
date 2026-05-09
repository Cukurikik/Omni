// OMNI System Layer: High-Performance Tensor Allocator
// Designed in Rust for absolute memory safety and zero-copy abstraction across the FFI boundary.

use std::alloc::{GlobalAlloc, Layout, System};
use std::ptr::NonNull;
use std::sync::atomic::{AtomicUsize, Ordering};

// OMNI Error type
#[derive(Debug)]
pub enum AllocatorError {
    AllocationFailed,
    InvalidLayout,
}

pub type OmniResult<T> = Result<T, AllocatorError>;

pub struct OmniTensorAllocator {
    total_allocated: AtomicUsize,
}

impl OmniTensorAllocator {
    pub const fn new() -> Self {
        OmniTensorAllocator {
            total_allocated: AtomicUsize::new(0),
        }
    }

    /// Allocates memory aligned for AVX-512 / GPU staging
    pub fn allocate_tensor_buffer(&self, size: usize, align: usize) -> OmniResult<NonNull<u8>> {
        if align == 0 || !align.is_power_of_two() {
            return Err(AllocatorError::InvalidLayout);
        }

        let layout = Layout::from_size_align(size, align)
            .map_err(|_| AllocatorError::InvalidLayout)?;

        // Unsafe block tightly constrained for performance
        let ptr = unsafe {
            // Using standard System allocator for the skeleton, 
            // production uses jemalloc or mimalloc tailored blocks.
            System.alloc(layout)
        };

        let non_null_ptr = NonNull::new(ptr).ok_or(AllocatorError::AllocationFailed)?;
        
        self.total_allocated.fetch_add(size, Ordering::SeqCst);
        Ok(non_null_ptr)
    }

    pub fn deallocate_tensor_buffer(&self, ptr: NonNull<u8>, size: usize, align: usize) -> OmniResult<()> {
        let layout = Layout::from_size_align(size, align)
            .map_err(|_| AllocatorError::InvalidLayout)?;

        unsafe {
            System.dealloc(ptr.as_ptr(), layout);
        }
        
        self.total_allocated.fetch_sub(size, Ordering::SeqCst);
        Ok(())
    }

    pub fn get_total_allocated_bytes(&self) -> usize {
        self.total_allocated.load(Ordering::SeqCst)
    }
}

// Global instance for C FFI bindings
pub static OMNI_GLOBAL_ALLOCATOR: OmniTensorAllocator = OmniTensorAllocator::new();

#[no_mangle]
pub extern "C" fn omni_allocate_tensor(size: usize) -> *mut u8 {
    match OMNI_GLOBAL_ALLOCATOR.allocate_tensor_buffer(size, 64) {
        Ok(ptr) => ptr.as_ptr(),
        Err(_) => std::ptr::null_mut(),
    }
}

#[no_mangle]
pub extern "C" fn omni_deallocate_tensor(ptr: *mut u8, size: usize) {
    if let Some(non_null) = NonNull::new(ptr) {
        let _ = OMNI_GLOBAL_ALLOCATOR.deallocate_tensor_buffer(non_null, size, 64);
    }
}
