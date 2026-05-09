//=============================================================================
// OMNI SYSTEM LAYER — ZERO-PAUSE GARBAGE COLLECTOR (RUST)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: Omni-specific GC logic. Uses deferred drop queues to ensure 
//              deallocation of massive tensors never blocks the main compute 
//              or network threads.
//=============================================================================

use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

/// Trait for items that can be dropped asynchronously
pub trait DeferredDrop: Send + 'static {
    fn drop_now(&mut self);
}

pub struct ZeroPauseGC {
    queue: Arc<Mutex<Vec<Box<dyn DeferredDrop>>>>,
}

impl ZeroPauseGC {
    pub fn new() -> Self {
        let queue = Arc::new(Mutex::new(Vec::new()));
        let q_clone = Arc::clone(&queue);

        // Background sweeper thread
        thread::spawn(move || {
            loop {
                thread::sleep(Duration::from_millis(100)); // Tick every 100ms
                
                let mut batch = Vec::new();
                {
                    let mut lock = q_clone.lock().unwrap();
                    if !lock.is_empty() {
                        // Take up to 50 items per tick to avoid CPU spikes
                        let count = std::cmp::min(lock.len(), 50);
                        batch.extend(lock.drain(0..count));
                    }
                }

                // Actually drop the items outside the lock
                for mut item in batch {
                    item.drop_now();
                }
            }
        });

        Self { queue }
    }

    /// Submits an item to be dropped later by the background thread.
    /// O(1) non-blocking operation for the calling thread.
    pub fn schedule_drop<T: DeferredDrop>(&self, item: T) {
        let mut q = self.queue.lock().unwrap();
        q.push(Box::new(item));
    }
}

// Example usage wrapper for a raw tensor pointer
pub struct TensorDropper {
    ptr: *mut u8,
    size: usize,
}

unsafe impl Send for TensorDropper {}

impl DeferredDrop for TensorDropper {
    fn drop_now(&mut self) {
        if !self.ptr.is_null() {
            unsafe {
                let layout = std::alloc::Layout::from_size_align(self.size, 64).unwrap();
                std::alloc::dealloc(self.ptr, layout);
            }
        }
    }
}
