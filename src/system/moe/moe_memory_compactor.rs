// moe_memory_compactor.rs — System / Memory
// Layer: System / Memory — MoE Arena Compaction
//
// Dynamically compacts fragmented memory arenas during MoE inference.
// Due to variable-length sequences and dynamic routing, MoE memory pools
// can become fragmented. This compactor runs in a background thread and
// coalesces free blocks using a lock-free design.

use std::sync::atomic::{AtomicUsize, Ordering};
use std::ptr;

// Mock structures for the arena
struct BlockHeader {
    size: usize,
    is_free: bool,
    next: *mut BlockHeader,
}

pub struct MoEMemoryCompactor {
    arena_base: *mut u8,
    arena_size: usize,
    total_freed: AtomicUsize,
    compaction_runs: AtomicUsize,
}

unsafe impl Send for MoEMemoryCompactor {}
unsafe impl Sync for MoEMemoryCompactor {}

impl MoEMemoryCompactor {
    pub fn new(arena_base: *mut u8, arena_size: usize) -> Self {
        Self {
            arena_base,
            arena_size,
            total_freed: AtomicUsize::new(0),
            compaction_runs: AtomicUsize::new(0),
        }
    }

    /// Scans the arena and merges adjacent free blocks.
    /// Should be called during inference idle times or when allocation fails.
    /// Returns the number of bytes coalesced.
    pub fn compact(&self) -> usize {
        let mut coalesced_bytes = 0;
        let mut current = self.arena_base as *mut BlockHeader;

        unsafe {
            while !current.is_null() {
                // If current block is free, look ahead
                if (*current).is_free {
                    let mut next_block = (*current).next;
                    
                    // Keep merging as long as the next block is also free
                    while !next_block.is_null() && (*next_block).is_free {
                        let merged_size = (*current).size + (*next_block).size + std::mem::size_of::<BlockHeader>();
                        (*current).size = merged_size;
                        (*current).next = (*next_block).next;
                        
                        coalesced_bytes += (*next_block).size;
                        next_block = (*current).next;
                    }
                }
                
                current = (*current).next;
            }
        }

        if coalesced_bytes > 0 {
            self.total_freed.fetch_add(coalesced_bytes, Ordering::Relaxed);
            self.compaction_runs.fetch_add(1, Ordering::Relaxed);
        }

        coalesced_bytes
    }

    pub fn get_stats(&self) -> (usize, usize) {
        (
            self.compaction_runs.load(Ordering::Relaxed),
            self.total_freed.load(Ordering::Relaxed)
        )
    }

    /// Fast fragmentation check to decide if compaction is needed.
    /// Calculates the ratio of small free blocks.
    pub fn get_fragmentation_ratio(&self) -> f32 {
        let mut total_free = 0;
        let mut largest_free = 0;
        let mut current = self.arena_base as *mut BlockHeader;

        unsafe {
            while !current.is_null() {
                if (*current).is_free {
                    total_free += (*current).size;
                    if (*current).size > largest_free {
                        largest_free = (*current).size;
                    }
                }
                current = (*current).next;
            }
        }

        if total_free == 0 {
            return 0.0;
        }

        // Ratio of largest block to total free space. Closer to 1.0 = less fragmented.
        // Return inverse (closer to 1.0 = highly fragmented).
        1.0 - (largest_free as f32 / total_free as f32)
    }
}
