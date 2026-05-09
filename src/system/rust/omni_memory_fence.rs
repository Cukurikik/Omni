use std::sync::atomic::{compiler_fence, Ordering};

// OMNI MOTHER: Memory Fences
// Prevents compiler instruction reordering in critical lock-free tensor operations.

pub struct OmniMemoryFence;

impl OmniMemoryFence {
    #[inline(always)]
    pub fn acquire() {
        compiler_fence(Ordering::Acquire);
    }

    #[inline(always)]
    pub fn release() {
        compiler_fence(Ordering::Release);
    }

    #[inline(always)]
    pub fn seq_cst() {
        compiler_fence(Ordering::SeqCst);
    }
}
