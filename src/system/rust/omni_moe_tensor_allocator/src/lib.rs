//! OMNI Framework - MoE Tensor Allocator (Rust)
//! A custom, high-performance memory allocator for Mixture of Experts.
//! This intercepts allocation requests for dynamic tensors during decoding
//! to prevent memory fragmentation and ensure pinned memory for P2P transfers.

use std::alloc::{GlobalAlloc, Layout, System};
use std::ffi::c_void;
use std::sync::atomic::{AtomicUsize, Ordering};

/// A custom allocator that distinguishes between standard host memory
/// and page-locked (pinned) memory used for rapid DMA transfers to GPUs.
pub struct OmniMoEAllocator {
    pinned_allocated: AtomicUsize,
    standard_allocated: AtomicUsize,
}

impl OmniMoEAllocator {
    pub const fn new() -> Self {
        OmniMoEAllocator {
            pinned_allocated: AtomicUsize::new(0),
            standard_allocated: AtomicUsize::new(0),
        }
    }

    pub fn get_pinned_usage(&self) -> usize {
        self.pinned_allocated.load(Ordering::Relaxed)
    }
}

unsafe impl GlobalAlloc for OmniMoEAllocator {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        // In a real implementation, we would check if the requested layout
        // is meant for a Tensor (e.g., via size thresholds or custom thread locals)
        // and invoke cudaHostAlloc. For this implementation, we wrap System alloc
        // while tracking stats.
        
        let ptr = System.alloc(layout);
        if !ptr.is_null() {
            self.standard_allocated.fetch_add(layout.size(), Ordering::Relaxed);
        }
        ptr
    }

    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        System.dealloc(ptr, layout);
        self.standard_allocated.fetch_sub(layout.size(), Ordering::Relaxed);
    }
}

#[global_allocator]
static GLOBAL_ALLOCATOR: OmniMoEAllocator = OmniMoEAllocator::new();

#[no_mangle]
pub extern "C" fn omni_get_memory_usage() -> usize {
    GLOBAL_ALLOCATOR.standard_allocated.load(Ordering::Relaxed)
}

#[no_mangle]
pub extern "C" fn omni_allocate_pinned_tensor(size: usize) -> *mut c_void {
    // Mocking cudaHostAlloc for production structure
    // unsafe {
    //     let mut ptr: *mut c_void = std::ptr::null_mut();
    //     cudaHostAlloc(&mut ptr, size, cudaHostAllocPortable);
    //     ptr
    // }
    
    // Fallback to standard alloc for standalone compilation
    unsafe {
        let layout = Layout::from_size_align(size, 64).unwrap();
        let ptr = System.alloc(layout) as *mut c_void;
        if !ptr.is_null() {
            GLOBAL_ALLOCATOR.pinned_allocated.fetch_add(size, Ordering::Relaxed);
        }
        ptr
    }
}

#[no_mangle]
pub extern "C" fn omni_free_pinned_tensor(ptr: *mut c_void, size: usize) {
    // Mocking cudaFreeHost
    // unsafe { cudaFreeHost(ptr); }
    
    unsafe {
        let layout = Layout::from_size_align(size, 64).unwrap();
        System.dealloc(ptr as *mut u8, layout);
        GLOBAL_ALLOCATOR.pinned_allocated.fetch_sub(size, Ordering::Relaxed);
    }
}
