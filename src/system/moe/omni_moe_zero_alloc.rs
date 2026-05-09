use std::sync::atomic::{AtomicUsize, Ordering};

pub struct ZeroCopyAllocator {
    offset: AtomicUsize,
    capacity: usize,
    base_ptr: *mut u8,
}

unsafe impl Send for ZeroCopyAllocator {}
unsafe impl Sync for ZeroCopyAllocator {}

impl ZeroCopyAllocator {
    pub fn new(capacity: usize, base_ptr: *mut u8) -> Self {
        Self { offset: AtomicUsize::new(0), capacity, base_ptr }
    }

    pub fn alloc(&self, size: usize) -> Option<*mut u8> {
        let old = self.offset.fetch_add(size, Ordering::Acquire);
        if old + size > self.capacity {
            None
        } else {
            Some(unsafe { self.base_ptr.add(old) })
        }
    }
}
