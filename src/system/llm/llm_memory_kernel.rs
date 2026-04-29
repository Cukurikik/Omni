// OMNI MOTHER - SYSTEM LAYER (RUST)
// ZERO MOCK - PRODUCTION READY
// Learnt from: Ray, LlamaFactory, LLMs-from-scratch
use std::sync::atomic::{AtomicUsize, Ordering};
use std::alloc::{alloc, dealloc, Layout};
use std::ptr::NonNull;

/// OmniResult enforces Monadic Error Handling across all layers
pub type OmniResult<T, E> = Result<T, E>;

#[derive(Debug)]
pub enum MemoryError {
    AllocationFailed,
    OutOfBoundsAccess,
    InvalidAlignment,
}

/// Zero-copy memory pool for ultra-fast LLM tensor allocations
pub struct LLMMemoryPool {
    base_ptr: NonNull<u8>,
    capacity: usize,
    offset: AtomicUsize,
    layout: Layout,
}

// Ensure thread safety for OMNI Concurrency Layer
unsafe impl Send for LLMMemoryPool {}
unsafe impl Sync for LLMMemoryPool {}

impl LLMMemoryPool {
    pub fn new(size_in_bytes: usize) -> OmniResult<Self, MemoryError> {
        let layout = Layout::from_size_align(size_in_bytes, 64)
            .map_err(|_| MemoryError::InvalidAlignment)?;
            
        let ptr = unsafe { alloc(layout) };
        
        let base_ptr = NonNull::new(ptr).ok_or(MemoryError::AllocationFailed)?;
        
        Ok(Self {
            base_ptr,
            capacity: size_in_bytes,
            offset: AtomicUsize::new(0),
            layout,
        })
    }

    /// Allocates memory for a tensor without copying data
    pub fn allocate_tensor(&self, size: usize) -> OmniResult<*mut u8, MemoryError> {
        // Align to 64 bytes for AVX-512 / ARM NEON
        let aligned_size = (size + 63) & !63;
        
        let current_offset = self.offset.fetch_add(aligned_size, Ordering::SeqCst);
        
        if current_offset + aligned_size > self.capacity {
            // Revert offset if out of memory
            self.offset.fetch_sub(aligned_size, Ordering::SeqCst);
            return Err(MemoryError::AllocationFailed);
        }
        
        unsafe {
            Ok(self.base_ptr.as_ptr().add(current_offset))
        }
    }
    
    pub fn reset(&self) {
        self.offset.store(0, Ordering::SeqCst);
    }
}

impl Drop for LLMMemoryPool {
    fn drop(&mut self) {
        unsafe {
            dealloc(self.base_ptr.as_ptr(), self.layout);
        }
    }
}

/// Omni Bridge export for C++ / Python / Go to use this pool
#[no_mangle]
pub extern "C" fn omni_create_memory_pool(size: usize) -> *mut LLMMemoryPool {
    match LLMMemoryPool::new(size) {
        Ok(pool) => Box::into_raw(Box::new(pool)),
        Err(_) => std::ptr::null_mut(),
    }
}
