// OMNI System Layer: Rust Thread Pool
use std::thread;

pub struct OmniThreadPool {
    workers: Vec<thread::JoinHandle<()>>,
}

impl OmniThreadPool {
    pub fn new(size: usize) -> Self {
        let mut workers = Vec::with_capacity(size);
        for _ in 0..size {
            workers.push(thread::spawn(|| {
                // worker loop
            }));
        }
        OmniThreadPool { workers }
    }
}
