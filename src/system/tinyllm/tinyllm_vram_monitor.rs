use std::sync::atomic::{AtomicUsize, Ordering};

/// OMNI Monadic Result
pub enum OmniResult<T, E> {
    Ok(T),
    Err(E),
}

/// Global VRAM Monitor Daemon for TinyLLM
pub struct VramMonitor {
    max_vram_mb: usize,
    allocated_mb: AtomicUsize,
}

impl VramMonitor {
    pub const fn new(max_mb: usize) -> Self {
        Self {
            max_vram_mb: max_mb,
            allocated_mb: AtomicUsize::new(0),
        }
    }

    pub fn request_allocation(&self, mb: usize) -> OmniResult<(), &'static str> {
        let current = self.allocated_mb.load(Ordering::SeqCst);
        if current + mb > self.max_vram_mb {
            return OmniResult::Err("OMNI_OOM: VRAM limit exceeded by TinyLLM allocation request.");
        }
        
        // Compare and swap to ensure thread-safety without locks
        match self.allocated_mb.compare_exchange_weak(
            current,
            current + mb,
            Ordering::SeqCst,
            Ordering::Relaxed,
        ) {
            Ok(_) => OmniResult::Ok(()),
            Err(_) => self.request_allocation(mb), // Retry on contention
        }
    }

    pub fn free_allocation(&self, mb: usize) {
        self.allocated_mb.fetch_sub(mb, Ordering::SeqCst);
    }
}

pub static GLOBAL_VRAM_MONITOR: VramMonitor = VramMonitor::new(8192); // 8GB system limit
