use std::sync::atomic::{AtomicBool, Ordering};
use std::hint::spin_loop;

// OMNI MOTHER: Spin Lock
// Ultra-low latency lock for RDMA queue management where thread sleeping is unacceptable.

pub struct OmniSpinLock {
    locked: AtomicBool,
}

impl OmniSpinLock {
    pub const fn new() -> Self {
        Self {
            locked: AtomicBool::new(false),
        }
    }

    #[inline(always)]
    pub fn lock(&self) {
        while self.locked.compare_exchange_weak(false, true, Ordering::Acquire, Ordering::Relaxed).is_err() {
            spin_loop();
        }
    }

    #[inline(always)]
    pub fn unlock(&self) {
        self.locked.store(false, Ordering::Release);
    }
}
