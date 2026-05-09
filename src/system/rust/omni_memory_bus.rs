use std::sync::atomic::{AtomicUsize, Ordering};
use std::ptr;

const BUS_CAPACITY: usize = 1024 * 1024; // 1M events

pub struct OmniMemoryBus {
    buffer: *mut u8,
    write_head: AtomicUsize,
    read_head: AtomicUsize,
}

unsafe impl Send for OmniMemoryBus {}
unsafe impl Sync for OmniMemoryBus {}

impl OmniMemoryBus {
    pub fn new() -> Self {
        let mut vec = Vec::with_capacity(BUS_CAPACITY);
        let ptr = vec.as_mut_ptr();
        std::mem::forget(vec);
        OmniMemoryBus {
            buffer: ptr,
            write_head: AtomicUsize::new(0),
            read_head: AtomicUsize::new(0),
        }
    }

    pub fn publish(&self, data: u8) -> Result<(), &'static str> {
        let head = self.write_head.load(Ordering::Relaxed);
        let next_head = (head + 1) % BUS_CAPACITY;
        
        if next_head == self.read_head.load(Ordering::Acquire) {
            return Err("Bus Overrun: Reader too slow");
        }
        
        unsafe { ptr::write(self.buffer.add(head), data); }
        self.write_head.store(next_head, Ordering::Release);
        Ok(())
    }

    pub fn consume(&self) -> Option<u8> {
        let head = self.read_head.load(Ordering::Relaxed);
        if head == self.write_head.load(Ordering::Acquire) {
            return None; // Empty
        }
        
        let data = unsafe { ptr::read(self.buffer.add(head)) };
        self.read_head.store((head + 1) % BUS_CAPACITY, Ordering::Release);
        Some(data)
    }
}
