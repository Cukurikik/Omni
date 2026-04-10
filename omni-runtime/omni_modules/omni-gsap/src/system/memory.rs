use std::alloc::{alloc, dealloc, Layout};
use std::ptr::NonNull;
use std::sync::atomic::{AtomicUsize, Ordering};

pub struct ArenaPool {
    base: NonNull<u8>,
    capacity: usize,
    offset: AtomicUsize,
    generation: AtomicUsize,
}

pub struct ArenaBlock { ptr: *mut u8, len: usize, gen: usize }

impl ArenaPool {
    pub fn new(capacity: usize) -> Result<Self, AllocError> {
        let layout = Layout::from_size_align(capacity, 64).map_err(|_| AllocError::InvalidLayout)?;
        let ptr = unsafe { alloc(layout) };
        let base = NonNull::new(ptr).ok_or(AllocError::OutOfMemory)?;
        Ok(Self { base, capacity, offset: AtomicUsize::new(0), generation: AtomicUsize::new(0) })
    }

    pub fn alloc(&self, size: usize) -> Result<ArenaBlock, AllocError> {
        let aligned = (size + 63) & !63;
        let off = self.offset.fetch_add(aligned, Ordering::SeqCst);
        if off + aligned > self.capacity { return Err(AllocError::OutOfMemory) }
        let ptr = unsafe { self.base.as_ptr().add(off) };
        Ok(ArenaBlock { ptr, len: size, gen: self.generation.load(Ordering::Relaxed) })
    }

    pub fn reset(&self) {
        self.offset.store(0, Ordering::SeqCst);
        self.generation.fetch_add(1, Ordering::SeqCst);
    }

    pub fn used(&self) -> usize { self.offset.load(Ordering::Relaxed) }
    pub fn remaining(&self) -> usize { self.capacity - self.used() }
}

#[derive(Debug)]
pub enum AllocError { OutOfMemory, InvalidLayout, DoubleFree }