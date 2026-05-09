// omni_tensor_arena.rs — Zero-Copy Tensor Memory Arena
// Inspired by: Memformer memory management + ONNX Runtime arena allocator
// Layer: System / Rust
//
// Bump allocator for inference tensor scratch space with automatic
// lifetime management and zero fragmentation.

use std::alloc::{alloc_zeroed, dealloc, Layout};
use std::cell::Cell;
use std::marker::PhantomData;
use std::ptr::NonNull;

/// Alignment for SIMD operations (AVX-512 = 64 bytes)
const ARENA_ALIGNMENT: usize = 64;

/// A bump-allocating arena for temporary tensor buffers.
///
/// All allocations are freed at once when the arena is reset,
/// making it ideal for inference scratch space.
pub struct TensorArena {
    base: NonNull<u8>,
    capacity: usize,
    offset: Cell<usize>,
    layout: Layout,
    peak_usage: Cell<usize>,
    allocation_count: Cell<u64>,
}

unsafe impl Send for TensorArena {}

/// A typed view into arena-allocated memory
pub struct ArenaSlice<'a, T> {
    ptr: *mut T,
    len: usize,
    _marker: PhantomData<&'a T>,
}

impl<'a, T> ArenaSlice<'a, T> {
    pub fn as_slice(&self) -> &[T] {
        unsafe { std::slice::from_raw_parts(self.ptr, self.len) }
    }

    pub fn as_mut_slice(&mut self) -> &mut [T] {
        unsafe { std::slice::from_raw_parts_mut(self.ptr, self.len) }
    }

    pub fn len(&self) -> usize {
        self.len
    }

    pub fn is_empty(&self) -> bool {
        self.len == 0
    }

    pub fn as_ptr(&self) -> *const T {
        self.ptr as *const T
    }

    pub fn as_mut_ptr(&mut self) -> *mut T {
        self.ptr
    }

    pub fn fill(&mut self, value: T) where T: Copy {
        for i in 0..self.len {
            unsafe { self.ptr.add(i).write(value); }
        }
    }

    pub fn copy_from_slice(&mut self, src: &[T]) where T: Copy {
        assert_eq!(src.len(), self.len, "Slice length mismatch");
        unsafe {
            std::ptr::copy_nonoverlapping(src.as_ptr(), self.ptr, self.len);
        }
    }
}

impl<'a, T> std::ops::Index<usize> for ArenaSlice<'a, T> {
    type Output = T;
    fn index(&self, idx: usize) -> &T {
        assert!(idx < self.len);
        unsafe { &*self.ptr.add(idx) }
    }
}

impl<'a, T> std::ops::IndexMut<usize> for ArenaSlice<'a, T> {
    fn index_mut(&mut self, idx: usize) -> &mut T {
        assert!(idx < self.len);
        unsafe { &mut *self.ptr.add(idx) }
    }
}

impl TensorArena {
    /// Create a new arena with the given capacity in bytes
    pub fn new(capacity_bytes: usize) -> Self {
        let layout = Layout::from_size_align(capacity_bytes, ARENA_ALIGNMENT)
            .expect("Invalid arena layout");
        let base = unsafe { alloc_zeroed(layout) };
        let base = NonNull::new(base).expect("Arena allocation failed");

        Self {
            base,
            capacity: capacity_bytes,
            offset: Cell::new(0),
            layout,
            peak_usage: Cell::new(0),
            allocation_count: Cell::new(0),
        }
    }

    /// Allocate a typed slice from the arena
    pub fn alloc_slice<T>(&self, count: usize) -> Option<ArenaSlice<'_, T>> {
        let size = count * std::mem::size_of::<T>();
        let align = std::mem::align_of::<T>().max(ARENA_ALIGNMENT);

        let current = self.offset.get();
        let aligned = (current + align - 1) & !(align - 1);
        let new_offset = aligned + size;

        if new_offset > self.capacity {
            return None;
        }

        self.offset.set(new_offset);
        self.allocation_count.set(self.allocation_count.get() + 1);

        let peak = self.peak_usage.get();
        if new_offset > peak {
            self.peak_usage.set(new_offset);
        }

        let ptr = unsafe { self.base.as_ptr().add(aligned) as *mut T };
        Some(ArenaSlice {
            ptr,
            len: count,
            _marker: PhantomData,
        })
    }

    /// Allocate a zeroed f32 buffer for tensor computation
    pub fn alloc_f32(&self, count: usize) -> Option<ArenaSlice<'_, f32>> {
        let mut slice = self.alloc_slice::<f32>(count)?;
        slice.fill(0.0);
        Some(slice)
    }

    /// Reset the arena, freeing all allocations at once (O(1))
    pub fn reset(&self) {
        self.offset.set(0);
        self.allocation_count.set(0);
    }

    /// Current bytes used
    pub fn used_bytes(&self) -> usize {
        self.offset.get()
    }

    /// Remaining bytes available
    pub fn remaining_bytes(&self) -> usize {
        self.capacity - self.offset.get()
    }

    /// Peak memory usage since creation
    pub fn peak_bytes(&self) -> usize {
        self.peak_usage.get()
    }

    /// Number of active allocations
    pub fn allocation_count(&self) -> u64 {
        self.allocation_count.get()
    }

    /// Total capacity
    pub fn capacity(&self) -> usize {
        self.capacity
    }
}

impl Drop for TensorArena {
    fn drop(&mut self) {
        unsafe {
            dealloc(self.base.as_ptr(), self.layout);
        }
    }
}

/// Scoped arena checkpoint — allows partial rollback
pub struct ArenaCheckpoint<'a> {
    arena: &'a TensorArena,
    saved_offset: usize,
    saved_count: u64,
}

impl<'a> ArenaCheckpoint<'a> {
    pub fn new(arena: &'a TensorArena) -> Self {
        Self {
            arena,
            saved_offset: arena.offset.get(),
            saved_count: arena.allocation_count.get(),
        }
    }
}

impl<'a> Drop for ArenaCheckpoint<'a> {
    fn drop(&mut self) {
        self.arena.offset.set(self.saved_offset);
        self.arena.allocation_count.set(self.saved_count);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_arena_alloc_and_reset() {
        let arena = TensorArena::new(1024 * 1024); // 1MB

        let mut buf = arena.alloc_f32(256).unwrap();
        assert_eq!(buf.len(), 256);
        buf[0] = 42.0;
        assert_eq!(buf[0], 42.0);

        assert!(arena.used_bytes() > 0);
        arena.reset();
        assert_eq!(arena.used_bytes(), 0);
    }

    #[test]
    fn test_arena_checkpoint() {
        let arena = TensorArena::new(4096);
        let _a = arena.alloc_f32(64).unwrap();
        let used_before = arena.used_bytes();

        {
            let _cp = ArenaCheckpoint::new(&arena);
            let _b = arena.alloc_f32(64).unwrap();
            assert!(arena.used_bytes() > used_before);
        }
        // Checkpoint restores on drop
        assert_eq!(arena.used_bytes(), used_before);
    }

    #[test]
    fn test_arena_overflow() {
        let arena = TensorArena::new(256);
        let result = arena.alloc_f32(1000);
        assert!(result.is_none());
    }
}
