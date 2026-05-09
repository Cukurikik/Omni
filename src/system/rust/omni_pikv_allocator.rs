// OMNI MOTHER: Rust PiKV Allocator
// Memory-safe, high-performance physical block allocator for KV Cache

use std::sync::Mutex;
use std::collections::VecDeque;

pub struct OmniPiKVRustAllocator {
    free_blocks: Mutex<VecDeque<u32>>,
    total_blocks: u32,
}

impl OmniPiKVRustAllocator {
    pub fn new(total_blocks: u32) -> Self {
        let mut queue = VecDeque::with_capacity(total_blocks as usize);
        for i in 0..total_blocks {
            queue.push_back(i);
        }
        Self {
            free_blocks: Mutex::new(queue),
            total_blocks,
        }
    }

    pub fn allocate(&self) -> Option<u32> {
        let mut blocks = self.free_blocks.lock().unwrap();
        blocks.pop_front()
    }

    pub fn free(&self, block_id: u32) {
        let mut blocks = self.free_blocks.lock().unwrap();
        blocks.push_back(block_id);
    }
}
