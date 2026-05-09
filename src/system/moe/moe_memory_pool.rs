// moe_memory_pool.rs — Lock-Free Memory Pool for MoE Token Buffers
// Layer: System / Memory — MoE Lock-Free Allocator
//
// Thread-safe, lock-free memory pool for token buffer allocation
// during MoE inference. Pre-allocates fixed-size blocks to avoid
// allocation overhead during expert computation hot paths.

use std::sync::atomic::{AtomicBool, AtomicU64, AtomicUsize, Ordering};
use std::sync::Arc;
use std::alloc::{alloc_zeroed, dealloc, Layout};
use std::ptr;

const CACHE_LINE: usize = 64;

/// A single memory block in the pool.
#[repr(C, align(64))]
struct PoolBlock {
    data: *mut u8,
    layout: Layout,
    in_use: AtomicBool,
    alloc_count: AtomicU64,
}

unsafe impl Send for PoolBlock {}
unsafe impl Sync for PoolBlock {}

impl PoolBlock {
    fn new(size: usize) -> Self {
        let layout = Layout::from_size_align(size, CACHE_LINE)
            .expect("Invalid layout");
        let data = unsafe { alloc_zeroed(layout) };
        assert!(!data.is_null(), "Allocation failed");
        Self {
            data,
            layout,
            in_use: AtomicBool::new(false),
            alloc_count: AtomicU64::new(0),
        }
    }

    fn try_acquire(&self) -> bool {
        self.in_use.compare_exchange(false, true, Ordering::Acquire, Ordering::Relaxed)
            .is_ok()
    }

    fn release(&self) {
        self.alloc_count.fetch_add(1, Ordering::Relaxed);
        self.in_use.store(false, Ordering::Release);
    }

    fn clear(&self) {
        unsafe { ptr::write_bytes(self.data, 0, self.layout.size()) };
    }
}

impl Drop for PoolBlock {
    fn drop(&mut self) {
        unsafe { dealloc(self.data, self.layout) };
    }
}

/// Pool statistics.
pub struct PoolStats {
    pub total_blocks: usize,
    pub in_use: usize,
    pub free: usize,
    pub total_allocations: u64,
    pub total_bytes: usize,
}

/// A handle to a borrowed buffer from the pool.
pub struct BufferHandle<'a> {
    block: &'a PoolBlock,
    pub ptr: *mut u8,
    pub size: usize,
}

impl<'a> BufferHandle<'a> {
    /// Get the buffer as a mutable slice.
    pub fn as_slice_mut(&mut self) -> &mut [u8] {
        unsafe { std::slice::from_raw_parts_mut(self.ptr, self.size) }
    }

    /// Get the buffer as a slice.
    pub fn as_slice(&self) -> &[u8] {
        unsafe { std::slice::from_raw_parts(self.ptr, self.size) }
    }
}

impl<'a> Drop for BufferHandle<'a> {
    fn drop(&mut self) {
        self.block.release();
    }
}

/// Lock-free memory pool for MoE token buffers.
pub struct MoEMemoryPool {
    blocks: Vec<PoolBlock>,
    block_size: usize,
    search_hint: AtomicUsize,
}

impl MoEMemoryPool {
    /// Create a new pool with `num_blocks` blocks of `block_size` bytes.
    pub fn new(num_blocks: usize, block_size: usize) -> Self {
        let blocks = (0..num_blocks)
            .map(|_| PoolBlock::new(block_size))
            .collect();
        Self {
            blocks,
            block_size,
            search_hint: AtomicUsize::new(0),
        }
    }

    /// Acquire a buffer from the pool (lock-free).
    pub fn acquire(&self) -> Option<BufferHandle<'_>> {
        let n = self.blocks.len();
        let start = self.search_hint.load(Ordering::Relaxed) % n;

        for i in 0..n {
            let idx = (start + i) % n;
            let block = &self.blocks[idx];
            if block.try_acquire() {
                block.clear();
                self.search_hint.store((idx + 1) % n, Ordering::Relaxed);
                return Some(BufferHandle {
                    block,
                    ptr: block.data,
                    size: self.block_size,
                });
            }
        }
        None // Pool exhausted
    }

    /// Get pool statistics.
    pub fn stats(&self) -> PoolStats {
        let mut in_use = 0;
        let mut total_allocs = 0u64;
        for block in &self.blocks {
            if block.in_use.load(Ordering::Relaxed) {
                in_use += 1;
            }
            total_allocs += block.alloc_count.load(Ordering::Relaxed);
        }
        PoolStats {
            total_blocks: self.blocks.len(),
            in_use,
            free: self.blocks.len() - in_use,
            total_allocations: total_allocs,
            total_bytes: self.blocks.len() * self.block_size,
        }
    }

    pub fn block_size(&self) -> usize {
        self.block_size
    }

    pub fn capacity(&self) -> usize {
        self.blocks.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_acquire_release() {
        let pool = MoEMemoryPool::new(4, 1024);
        let stats = pool.stats();
        assert_eq!(stats.free, 4);

        let buf = pool.acquire().unwrap();
        assert_eq!(pool.stats().in_use, 1);
        drop(buf);
        assert_eq!(pool.stats().free, 4);
    }

    #[test]
    fn test_pool_exhaustion() {
        let pool = MoEMemoryPool::new(2, 256);
        let _b1 = pool.acquire().unwrap();
        let _b2 = pool.acquire().unwrap();
        assert!(pool.acquire().is_none());
    }

    #[test]
    fn test_buffer_write() {
        let pool = MoEMemoryPool::new(1, 64);
        let mut buf = pool.acquire().unwrap();
        let slice = buf.as_slice_mut();
        slice[0] = 42;
        slice[63] = 99;
        assert_eq!(buf.as_slice()[0], 42);
        assert_eq!(buf.as_slice()[63], 99);
    }

    #[test]
    fn test_concurrent_access() {
        use std::thread;
        let pool = Arc::new(MoEMemoryPool::new(8, 512));
        let mut handles = vec![];

        for _ in 0..4 {
            let p = Arc::clone(&pool);
            handles.push(thread::spawn(move || {
                for _ in 0..100 {
                    if let Some(mut buf) = p.acquire() {
                        buf.as_slice_mut()[0] = 1;
                        // auto-released on drop
                    }
                }
            }));
        }

        for h in handles {
            h.join().unwrap();
        }

        assert_eq!(pool.stats().free, 8);
    }
}
