// ===========================================================================
// OMNI SYSTEM LAYER — MEMORY MANAGER (ARENA ALLOCATOR)
// ===========================================================================
// Domain Layer   : System (Memory-safe concurrency, ownership model)
// Language        : Rust
// Function        : Custom arena-based memory allocator for OMNI runtime with
//                   region-scoped allocation, deferred deallocation, alignment
//                   control, and memory usage statistics tracking
// ===========================================================================

use std::alloc::{Layout, alloc, dealloc};
use std::ptr;
use std::fmt;

/// Memory alignment for allocations.
pub const ALIGNMENT: usize = 16;
/// Default arena block size: 1MB.
pub const DEFAULT_BLOCK_SIZE: usize = 1024 * 1024;

// ---- Block ----------------------------------------------------------------

/// A contiguous memory block within an arena.
struct Block {
    data: *mut u8,
    capacity: usize,
    used: usize,
    layout: Layout,
}

impl Block {
    /// Allocate a new block of the given size.
    fn new(capacity: usize) -> Option<Self> {
        let layout = Layout::from_size_align(capacity, ALIGNMENT).ok()?;
        let data = unsafe { alloc(layout) };
        if data.is_null() {
            return None;
        }
        Some(Block {
            data,
            capacity,
            used: 0,
            layout,
        })
    }

    /// Attempt to allocate `size` bytes from this block, aligned to `align`.
    fn allocate(&mut self, size: usize, align: usize) -> Option<*mut u8> {
        let current = self.data as usize + self.used;
        let aligned = (current + align - 1) & !(align - 1);
        let padding = aligned - current;
        let total = padding + size;

        if self.used + total > self.capacity {
            return None; // not enough space
        }

        self.used += total;
        Some(aligned as *mut u8)
    }

    /// How many bytes are still available.
    fn remaining(&self) -> usize {
        self.capacity.saturating_sub(self.used)
    }

    /// Utilization percentage.
    fn utilization(&self) -> f64 {
        if self.capacity == 0 {
            return 0.0;
        }
        (self.used as f64 / self.capacity as f64) * 100.0
    }

    /// Reset usage counter (does NOT free memory).
    fn reset(&mut self) {
        self.used = 0;
    }
}

impl Drop for Block {
    fn drop(&mut self) {
        if !self.data.is_null() {
            unsafe { dealloc(self.data, self.layout) };
        }
    }
}

// ---- Arena Allocator ------------------------------------------------------

/// Arena-based memory allocator. Allocations are O(1) bump-pointer.
/// Memory is freed in bulk when the arena is dropped or reset.
pub struct ArenaAllocator {
    blocks: Vec<Block>,
    default_block_size: usize,
    total_allocated: usize,
    allocation_count: u64,
}

impl ArenaAllocator {
    /// Create a new arena with the given default block size.
    pub fn new(block_size: usize) -> Self {
        println!("[MEM-OMNI-RS] Arena allocator initialized (block size: {}KB)", block_size / 1024);
        let mut arena = ArenaAllocator {
            blocks: Vec::new(),
            default_block_size: block_size,
            total_allocated: 0,
            allocation_count: 0,
        };
        // Pre-allocate first block
        if let Some(block) = Block::new(block_size) {
            arena.blocks.push(block);
        }
        arena
    }

    /// Allocate `size` bytes with the given alignment.
    pub fn alloc(&mut self, size: usize, align: usize) -> Option<*mut u8> {
        // Try current block first
        if let Some(block) = self.blocks.last_mut() {
            if let Some(ptr) = block.allocate(size, align) {
                self.total_allocated += size;
                self.allocation_count += 1;
                return Some(ptr);
            }
        }

        // Need a new block
        let block_size = std::cmp::max(self.default_block_size, size + align);
        let mut new_block = Block::new(block_size)?;
        let ptr = new_block.allocate(size, align)?;
        self.blocks.push(new_block);
        self.total_allocated += size;
        self.allocation_count += 1;
        Some(ptr)
    }

    /// Allocate and zero-initialize.
    pub fn alloc_zeroed(&mut self, size: usize, align: usize) -> Option<*mut u8> {
        let ptr = self.alloc(size, align)?;
        unsafe { ptr::write_bytes(ptr, 0, size) };
        Some(ptr)
    }

    /// Reset all blocks (reuse memory without deallocation).
    pub fn reset(&mut self) {
        for block in &mut self.blocks {
            block.reset();
        }
        self.total_allocated = 0;
        self.allocation_count = 0;
        println!("[MEM-OMNI-RS] Arena reset ({} blocks retained)", self.blocks.len());
    }

    // ---- Statistics -------------------------------------------------------

    pub fn stats(&self) -> ArenaStats {
        let total_capacity: usize = self.blocks.iter().map(|b| b.capacity).sum();
        let total_used: usize = self.blocks.iter().map(|b| b.used).sum();
        ArenaStats {
            block_count: self.blocks.len(),
            total_capacity_kb: total_capacity / 1024,
            total_used_kb: total_used / 1024,
            allocation_count: self.allocation_count,
            utilization_pct: if total_capacity > 0 {
                (total_used as f64 / total_capacity as f64) * 100.0
            } else {
                0.0
            },
        }
    }
}

impl Drop for ArenaAllocator {
    fn drop(&mut self) {
        let stats = self.stats();
        println!(
            "[MEM-OMNI-RS] Arena dropped: {} blocks, {}KB used/{}KB capacity ({:.1}%)",
            stats.block_count, stats.total_used_kb, stats.total_capacity_kb, stats.utilization_pct
        );
    }
}

#[derive(Debug)]
pub struct ArenaStats {
    pub block_count: usize,
    pub total_capacity_kb: usize,
    pub total_used_kb: usize,
    pub allocation_count: u64,
    pub utilization_pct: f64,
}

impl fmt::Display for ArenaStats {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(
            f,
            "Arena[blocks={}, used={}KB/{}KB ({:.1}%), allocs={}]",
            self.block_count, self.total_used_kb, self.total_capacity_kb,
            self.utilization_pct, self.allocation_count
        )
    }
}
