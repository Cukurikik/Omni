// OMNI System — Rust Zero-Copy Channel
// High-performance inter-thread communication without data copying

use std::sync::{Arc, Mutex, Condvar};
use std::collections::VecDeque;

pub struct OmniZeroCopyChannel<T> {
    queue: Mutex<VecDeque<*mut T>>,
    condvar: Condvar,
}

impl<T> OmniZeroCopyChannel<T> {
    pub fn new() -> Arc<Self> {
        Arc::new(OmniZeroCopyChannel {
            queue: Mutex::new(VecDeque::new()),
            condvar: Condvar::new(),
        })
    }

    pub fn send(&self, ptr: *mut T) {
        let mut q = self.queue.lock().unwrap();
        q.push_back(ptr);
        self.condvar.notify_one();
    }

    pub fn receive(&self) -> *mut T {
        let mut q = self.queue.lock().unwrap();
        while q.is_empty() {
            q = self.condvar.wait(q).unwrap();
        }
        q.pop_front().unwrap()
    }
}

// Safety: We assume the caller manages the raw pointer lifecycles correctly
// according to OMNI memory guidelines.
unsafe impl<T> Send for OmniZeroCopyChannel<T> {}
unsafe impl<T> Sync for OmniZeroCopyChannel<T> {}
