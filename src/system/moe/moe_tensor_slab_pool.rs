// moe_tensor_slab_pool.rs — System / Hardware
// Layer: System / Memory — VRAM Slab Allocator
//
// Dynamic MoE routing destroys CUDA memory via fragmentation. This module
// implements a pure Rust Slab Allocator. It pre-reserves monolithic VRAM blocks
// and hands out aligned, fixed-size memory slabs directly to the inference engine.

use std::collections::VecDeque;
use std::sync::Mutex;
use std::ptr::NonNull;

#[derive(Debug)]
pub enum AllocError {
    OutOfMemory,
    InvalidSize,
}

struct Slab {
    ptr: NonNull<u8>,
    is_free: bool,
}

unsafe impl Send for Slab {}
unsafe impl Sync for Slab {}

pub struct TensorSlabPool {
    slabs: Mutex<Vec<Slab>>,
    slab_size_bytes: usize,
    total_capacity_bytes: usize,
    base_ptr: NonNull<u8>,
}

impl TensorSlabPool {
    /// Initializes a monolithic slab allocator. In production, base_ptr is from cudaMalloc.
    pub unsafe fn new(base_ptr: *mut u8, total_capacity_bytes: usize, slab_size_bytes: usize) -> Result<Self, AllocError> {
        if base_ptr.is_null() || slab_size_bytes == 0 || total_capacity_bytes % slab_size_bytes != 0 {
            return Err(AllocError::InvalidSize);
        }

        let num_slabs = total_capacity_bytes / slab_size_bytes;
        let mut slabs = Vec::with_capacity(num_slabs);

        for i in 0..num_slabs {
            let offset_ptr = base_ptr.add(i * slab_size_bytes);
            slabs.push(Slab {
                ptr: NonNull::new_unchecked(offset_ptr),
                is_free: true,
            });
        }

        Ok(TensorSlabPool {
            slabs: Mutex::new(slabs),
            slab_size_bytes,
            total_capacity_bytes,
            base_ptr: NonNull::new_unchecked(base_ptr),
        })
    }

    /// O(N) linear scan for a free slab. Fast enough since N is usually < 1024 for huge slabs.
    pub fn allocate_slab(&self) -> Result<NonNull<u8>, AllocError> {
        let mut slabs = self.slabs.lock().unwrap();
        for slab in slabs.iter_mut() {
            if slab.is_free {
                slab.is_free = false;
                return Ok(slab.ptr);
            }
        }
        Err(AllocError::OutOfMemory)
    }

    /// Returns a slab to the pool.
    pub fn free_slab(&self, ptr_to_free: NonNull<u8>) {
        let mut slabs = self.slabs.lock().unwrap();
        for slab in slabs.iter_mut() {
            if slab.ptr == ptr_to_free {
                slab.is_free = true;
                return;
            }
        }
        panic!("FATAL: Attempted to free a pointer not owned by this Slab Pool!");
    }
}
