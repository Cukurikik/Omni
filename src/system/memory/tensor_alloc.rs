// OMNI System Layer — Rust Tensor Memory Allocator
// Zero-copy memory management for transformer inference.
// Learned from: Rust ownership model, huggingface/candle patterns

use std::alloc::{alloc, dealloc, Layout};
use std::ptr::NonNull;
use std::sync::atomic::{AtomicUsize, Ordering};

/// Alignment for SIMD-friendly tensor storage (64-byte for AVX-512)
const TENSOR_ALIGNMENT: usize = 64;

/// Reference-counted tensor buffer for zero-copy data transfer
pub struct TensorBuffer {
    ptr: NonNull<u8>,
    layout: Layout,
    len: usize,
    ref_count: AtomicUsize,
}

impl TensorBuffer {
    /// Allocate a new aligned tensor buffer
    pub fn new(size_bytes: usize) -> Result<Self, TensorAllocError> {
        if size_bytes == 0 {
            return Err(TensorAllocError::ZeroSize);
        }
        let layout = Layout::from_size_align(size_bytes, TENSOR_ALIGNMENT)
            .map_err(|_| TensorAllocError::InvalidLayout)?;

        let ptr = unsafe { alloc(layout) };
        let ptr = NonNull::new(ptr).ok_or(TensorAllocError::OutOfMemory)?;

        Ok(Self {
            ptr,
            layout,
            len: size_bytes,
            ref_count: AtomicUsize::new(1),
        })
    }

    /// Create tensor buffer for specific dtype and shape
    pub fn for_shape(shape: &[usize], dtype_size: usize) -> Result<Self, TensorAllocError> {
        let numel: usize = shape.iter().product();
        let size = numel * dtype_size;
        Self::new(size)
    }

    /// Get raw pointer (unsafe — caller must ensure valid access)
    pub fn as_ptr(&self) -> *const u8 {
        self.ptr.as_ptr()
    }

    /// Get mutable pointer (unsafe — caller must ensure exclusive access)
    pub fn as_mut_ptr(&mut self) -> *mut u8 {
        self.ptr.as_ptr()
    }

    /// Buffer size in bytes
    pub fn len(&self) -> usize {
        self.len
    }

    /// Check if buffer is empty
    pub fn is_empty(&self) -> bool {
        self.len == 0
    }

    /// Increment reference count (for zero-copy sharing)
    pub fn clone_ref(&self) -> Self {
        self.ref_count.fetch_add(1, Ordering::Relaxed);
        Self {
            ptr: self.ptr,
            layout: self.layout,
            len: self.len,
            ref_count: AtomicUsize::new(self.ref_count.load(Ordering::Relaxed)),
        }
    }

    /// Get as typed slice (unsafe — caller must ensure correct type)
    pub unsafe fn as_slice<T>(&self) -> &[T] {
        let count = self.len / std::mem::size_of::<T>();
        std::slice::from_raw_parts(self.ptr.as_ptr() as *const T, count)
    }

    /// Get as mutable typed slice
    pub unsafe fn as_mut_slice<T>(&mut self) -> &mut [T] {
        let count = self.len / std::mem::size_of::<T>();
        std::slice::from_raw_parts_mut(self.ptr.as_ptr() as *mut T, count)
    }
}

impl Drop for TensorBuffer {
    fn drop(&mut self) {
        if self.ref_count.fetch_sub(1, Ordering::Release) == 1 {
            std::sync::atomic::fence(Ordering::Acquire);
            unsafe { dealloc(self.ptr.as_ptr(), self.layout) };
        }
    }
}

// Safety: TensorBuffer can be sent across threads
unsafe impl Send for TensorBuffer {}
unsafe impl Sync for TensorBuffer {}

/// Error types for tensor allocation
#[derive(Debug)]
pub enum TensorAllocError {
    ZeroSize,
    InvalidLayout,
    OutOfMemory,
}

impl std::fmt::Display for TensorAllocError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::ZeroSize => write!(f, "Cannot allocate zero-size buffer"),
            Self::InvalidLayout => write!(f, "Invalid memory layout"),
            Self::OutOfMemory => write!(f, "Out of memory"),
        }
    }
}

impl std::error::Error for TensorAllocError {}

/// Memory pool for efficient tensor allocation/deallocation
pub struct TensorPool {
    pools: Vec<Vec<TensorBuffer>>,
    size_classes: Vec<usize>,
    total_allocated: AtomicUsize,
}

impl TensorPool {
    pub fn new() -> Self {
        // Pre-define size classes: 1KB, 4KB, 16KB, 64KB, 256KB, 1MB, 4MB, 16MB, 64MB
        let size_classes = vec![
            1024, 4096, 16384, 65536, 262144,
            1048576, 4194304, 16777216, 67108864,
        ];
        let pools = size_classes.iter().map(|_| Vec::new()).collect();
        Self {
            pools,
            size_classes,
            total_allocated: AtomicUsize::new(0),
        }
    }

    /// Allocate from pool or create new buffer
    pub fn allocate(&mut self, size: usize) -> Result<TensorBuffer, TensorAllocError> {
        let class_idx = self.size_classes.iter().position(|&s| s >= size);

        if let Some(idx) = class_idx {
            if let Some(buf) = self.pools[idx].pop() {
                return Ok(buf);
            }
            let alloc_size = self.size_classes[idx];
            self.total_allocated.fetch_add(alloc_size, Ordering::Relaxed);
            TensorBuffer::new(alloc_size)
        } else {
            self.total_allocated.fetch_add(size, Ordering::Relaxed);
            TensorBuffer::new(size)
        }
    }

    /// Return buffer to pool for reuse
    pub fn deallocate(&mut self, buf: TensorBuffer) {
        let size = buf.len();
        if let Some(idx) = self.size_classes.iter().position(|&s| s == size) {
            self.pools[idx].push(buf);
        }
        // Non-standard sizes are dropped normally
    }

    /// Total bytes currently allocated
    pub fn total_allocated(&self) -> usize {
        self.total_allocated.load(Ordering::Relaxed)
    }
}

impl Default for TensorPool {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tensor_buffer_allocation() {
        let buf = TensorBuffer::new(1024).unwrap();
        assert_eq!(buf.len(), 1024);
        assert!(!buf.is_empty());
    }

    #[test]
    fn test_tensor_pool() {
        let mut pool = TensorPool::new();
        let buf = pool.allocate(512).unwrap();
        assert!(buf.len() >= 512);
        pool.deallocate(buf);
    }

    #[test]
    fn test_for_shape() {
        let buf = TensorBuffer::for_shape(&[32, 128, 768], 4).unwrap();
        assert_eq!(buf.len(), 32 * 128 * 768 * 4);
    }
}
