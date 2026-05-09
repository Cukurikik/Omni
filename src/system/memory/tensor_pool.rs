//=============================================================================
// OMNI SYSTEM LAYER — ZERO-FRAGMENTATION TENSOR POOL (RUST)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: Memory pool for allocating tensors rapidly without OS overhead.
//=============================================================================

use std::alloc::{alloc, dealloc, Layout};
use std::ptr::NonNull;
use std::sync::Mutex;

/// OMNI IDIOM: Monadic error
#[derive(Debug)]
pub enum PoolError {
    OutOfMemory,
    InvalidSize,
}

pub type Result<T> = std::result::Result<T, PoolError>;

struct Chunk {
    ptr: NonNull<u8>,
    size: usize,
    in_use: bool,
}

/// A thread-safe memory pool tailored for Tensor dimension allocations.
pub struct TensorMemoryPool {
    chunks: Mutex<Vec<Chunk>>,
    chunk_size: usize,
}

impl TensorMemoryPool {
    pub fn new(chunk_size: usize, initial_chunks: usize) -> Result<Self> {
        let mut chunks = Vec::with_capacity(initial_chunks);
        let layout = Layout::from_size_align(chunk_size, 64)
            .map_err(|_| PoolError::InvalidSize)?;

        for _ in 0..initial_chunks {
            let ptr = unsafe { alloc(layout) };
            let non_null = NonNull::new(ptr).ok_or(PoolError::OutOfMemory)?;
            chunks.push(Chunk { ptr: non_null, size: chunk_size, in_use: false });
        }

        Ok(Self {
            chunks: Mutex::new(chunks),
            chunk_size,
        })
    }

    /// Acquires a chunk from the pool.
    pub fn acquire(&self) -> Result<NonNull<u8>> {
        let mut chunks = self.chunks.lock().unwrap();
        
        for chunk in chunks.iter_mut() {
            if !chunk.in_use {
                chunk.in_use = true;
                return Ok(chunk.ptr);
            }
        }
        
        Err(PoolError::OutOfMemory)
    }

    /// Releases a chunk back to the pool.
    pub fn release(&self, ptr: NonNull<u8>) {
        let mut chunks = self.chunks.lock().unwrap();
        
        for chunk in chunks.iter_mut() {
            if chunk.ptr == ptr {
                chunk.in_use = false;
                break;
            }
        }
    }
}
