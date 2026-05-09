use std::alloc::{GlobalAlloc, Layout, System};
use std::sync::atomic::{AtomicUsize, Ordering};

/// OMNI DeepSpeed Memory Pool
/// Zero-copy memory allocator for multi-GPU training tensors.

pub struct DeepSpeedMemoryPool {
    allocated_bytes: AtomicUsize,
    peak_bytes: AtomicUsize,
}

impl DeepSpeedMemoryPool {
    pub const fn new() -> Self {
        Self {
            allocated_bytes: AtomicUsize::new(0),
            peak_bytes: AtomicUsize::new(0),
        }
    }

    pub fn allocate_tensor(&self, size: usize) -> Result<*mut u8, &'static str> {
        if size == 0 {
            return Err("Cannot allocate 0 bytes for tensor");
        }
        
        let layout = Layout::from_size_align(size, 64).map_err(|_| "Invalid layout alignment")?;
        
        // Unsafe allocation block - OMNI System Layer
        let ptr = unsafe { System.alloc(layout) };
        if ptr.is_null() {
            return Err("OOM: Failed to allocate tensor memory");
        }
        
        let current = self.allocated_bytes.fetch_add(size, Ordering::SeqCst) + size;
        let mut peak = self.peak_bytes.load(Ordering::SeqCst);
        while current > peak {
            match self.peak_bytes.compare_exchange_weak(peak, current, Ordering::SeqCst, Ordering::SeqCst) {
                Ok(_) => break,
                Err(p) => peak = p,
            }
        }
        
        Ok(ptr)
    }

    pub fn deallocate_tensor(&self, ptr: *mut u8, size: usize) {
        if !ptr.is_null() && size > 0 {
            let layout = Layout::from_size_align(size, 64).unwrap();
            unsafe {
                System.dealloc(ptr, layout);
            }
            self.allocated_bytes.fetch_sub(size, Ordering::SeqCst);
        }
    }
    
    pub fn get_stats(&self) -> (usize, usize) {
        (
            self.allocated_bytes.load(Ordering::SeqCst),
            self.peak_bytes.load(Ordering::SeqCst)
        )
    }
}
