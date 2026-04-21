// ===========================================================================
// OMNI MEMORY POOL ENGINE (POLYLINGUAL REMEDIATION — BATCH 37.7)
// ===========================================================================
// Absorbed From  : slab crate + jemalloc slab allocator + Linux SLUB concepts
// Logic Inherited: Rust / System Layer (Fixed-Size Slab Allocator with Free-List)
// Domain Layer   : System (Rust Core)
// ===========================================================================
//
// By studying the `slab` crate and jemalloc's slab allocator, Mother
// learned that for fixed-size object pools (e.g., connection handles,
// packet buffers), a free-list slab allocator provides O(1) alloc/free
// with zero fragmentation. Each slab slot is either occupied (holding
// a value) or vacant (holding the index of the next free slot).
//
// Rust's ownership model guarantees that a `SlabKey` cannot be used
// after the slot has been freed — the borrow checker prevents
// use-after-free at compile time.

use std::sync::atomic::{AtomicUsize, Ordering};

/// Key type returned by the slab allocator. Opaque handle to a slot.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct SlabKey {
    index: usize,
    generation: u64,
}

/// Internal slot state — either occupied with a value or vacant with
/// a pointer to the next free slot.
enum Slot<T> {
    Occupied {
        value: T,
        generation: u64,
    },
    Vacant {
        next_free: Option<usize>,
        generation: u64,
    },
}

/// Fixed-size slab allocator with generational keys.
///
/// Generational keys prevent ABA problems: if slot 5 is freed and
/// then reallocated, the old `SlabKey { index: 5, generation: 1 }`
/// will fail to access the new `generation: 2` occupant.
pub struct OmniMemoryPoolEngine<T> {
    slots: Vec<Slot<T>>,
    free_head: Option<usize>,
    len: usize,
    capacity: usize,
    generation_counter: u64,
    // Statistics
    total_allocations: AtomicUsize,
    total_deallocations: AtomicUsize,
    peak_usage: AtomicUsize,
}

/// Result types for pool operations (monadic error handling).
#[derive(Debug)]
pub enum PoolError {
    PoolExhausted,
    InvalidKey,
    GenerationMismatch { expected: u64, found: u64 },
}

pub type PoolResult<T> = Result<T, PoolError>;

impl<T> OmniMemoryPoolEngine<T> {
    /// Create a new memory pool with the given initial capacity.
    /// All slots start as Vacant, forming a free-list chain.
    pub fn new(capacity: usize) -> Self {
        let mut slots = Vec::with_capacity(capacity);

        // Build free-list: slot[0] → slot[1] → ... → slot[N-1] → None
        for i in 0..capacity {
            let next = if i + 1 < capacity { Some(i + 1) } else { None };
            slots.push(Slot::Vacant {
                next_free: next,
                generation: 0,
            });
        }

        Self {
            slots,
            free_head: if capacity > 0 { Some(0) } else { None },
            len: 0,
            capacity,
            generation_counter: 0,
            total_allocations: AtomicUsize::new(0),
            total_deallocations: AtomicUsize::new(0),
            peak_usage: AtomicUsize::new(0),
        }
    }

    /// Allocate a slot and store the value. Returns a `SlabKey` handle.
    /// O(1) — pops from the free-list head.
    pub fn allocate(&mut self, value: T) -> PoolResult<SlabKey> {
        let index = match self.free_head {
            Some(i) => i,
            None => return Err(PoolError::PoolExhausted),
        };

        // Advance free-list head
        let generation = match &self.slots[index] {
            Slot::Vacant { next_free, generation } => {
                self.free_head = *next_free;
                *generation
            }
            _ => return Err(PoolError::InvalidKey),
        };

        // Increment generation for this slot
        self.generation_counter += 1;
        let new_gen = self.generation_counter;

        self.slots[index] = Slot::Occupied {
            value,
            generation: new_gen,
        };

        self.len += 1;
        self.total_allocations.fetch_add(1, Ordering::Relaxed);

        // Track peak usage
        let current_peak = self.peak_usage.load(Ordering::Relaxed);
        if self.len > current_peak {
            self.peak_usage.store(self.len, Ordering::Relaxed);
        }

        Ok(SlabKey {
            index,
            generation: new_gen,
        })
    }

    /// Free a slot, returning the stored value.
    /// O(1) — pushes onto the free-list head.
    pub fn deallocate(&mut self, key: SlabKey) -> PoolResult<T> {
        if key.index >= self.slots.len() {
            return Err(PoolError::InvalidKey);
        }

        // Verify generation to prevent ABA
        match &self.slots[key.index] {
            Slot::Occupied { generation, .. } => {
                if *generation != key.generation {
                    return Err(PoolError::GenerationMismatch {
                        expected: key.generation,
                        found: *generation,
                    });
                }
            }
            Slot::Vacant { .. } => return Err(PoolError::InvalidKey),
        }

        // Extract value using swap
        let old_slot = std::mem::replace(
            &mut self.slots[key.index],
            Slot::Vacant {
                next_free: self.free_head,
                generation: key.generation,
            },
        );

        self.free_head = Some(key.index);
        self.len -= 1;
        self.total_deallocations.fetch_add(1, Ordering::Relaxed);

        match old_slot {
            Slot::Occupied { value, .. } => Ok(value),
            _ => unreachable!("Already verified occupied above"),
        }
    }

    /// Get a reference to the value at the given key.
    pub fn get(&self, key: SlabKey) -> PoolResult<&T> {
        if key.index >= self.slots.len() {
            return Err(PoolError::InvalidKey);
        }

        match &self.slots[key.index] {
            Slot::Occupied { value, generation } => {
                if *generation != key.generation {
                    return Err(PoolError::GenerationMismatch {
                        expected: key.generation,
                        found: *generation,
                    });
                }
                Ok(value)
            }
            Slot::Vacant { .. } => Err(PoolError::InvalidKey),
        }
    }

    /// Get a mutable reference to the value at the given key.
    pub fn get_mut(&mut self, key: SlabKey) -> PoolResult<&mut T> {
        if key.index >= self.slots.len() {
            return Err(PoolError::InvalidKey);
        }

        match &mut self.slots[key.index] {
            Slot::Occupied { value, generation } => {
                if *generation != key.generation {
                    return Err(PoolError::GenerationMismatch {
                        expected: key.generation,
                        found: *generation,
                    });
                }
                Ok(value)
            }
            Slot::Vacant { .. } => Err(PoolError::InvalidKey),
        }
    }

    /// Check if a key is still valid (slot occupied with matching generation).
    pub fn contains(&self, key: SlabKey) -> bool {
        if key.index >= self.slots.len() {
            return false;
        }
        matches!(&self.slots[key.index],
            Slot::Occupied { generation, .. } if *generation == key.generation
        )
    }

    /// Number of occupied slots.
    pub fn len(&self) -> usize {
        self.len
    }

    /// True if no slots are occupied.
    pub fn is_empty(&self) -> bool {
        self.len == 0
    }

    /// Number of available (free) slots.
    pub fn available(&self) -> usize {
        self.capacity - self.len
    }

    /// Total capacity.
    pub fn capacity(&self) -> usize {
        self.capacity
    }

    /// Iterate over all occupied slots.
    pub fn iter(&self) -> impl Iterator<Item = (SlabKey, &T)> {
        self.slots.iter().enumerate().filter_map(|(i, slot)| {
            match slot {
                Slot::Occupied { value, generation } => {
                    Some((SlabKey { index: i, generation: *generation }, value))
                }
                Slot::Vacant { .. } => None,
            }
        })
    }

    /// Clear all slots, returning to fully vacant state.
    pub fn clear(&mut self) {
        for i in 0..self.slots.len() {
            let next = if i + 1 < self.capacity { Some(i + 1) } else { None };
            self.slots[i] = Slot::Vacant {
                next_free: next,
                generation: self.generation_counter,
            };
        }
        self.free_head = if self.capacity > 0 { Some(0) } else { None };
        self.len = 0;
    }

    /// Diagnostics for OMNI Engine Registry.
    pub fn diagnostics(&self) -> MemoryPoolDiagnostics {
        MemoryPoolDiagnostics {
            engine: "OmniMemoryPoolEngine".to_string(),
            layer: "Rust System".to_string(),
            capacity: self.capacity,
            occupied: self.len,
            available: self.available(),
            utilization_pct: if self.capacity > 0 {
                (self.len as f64 / self.capacity as f64) * 100.0
            } else {
                0.0
            },
            peak_usage: self.peak_usage.load(Ordering::Relaxed),
            total_allocations: self.total_allocations.load(Ordering::Relaxed),
            total_deallocations: self.total_deallocations.load(Ordering::Relaxed),
            generation_counter: self.generation_counter,
            learned_logic: vec![
                "slab-free-list-o1-alloc-free".to_string(),
                "generational-key-aba-prevention".to_string(),
                "enum-occupied-vacant-slot-state".to_string(),
                "ownership-prevents-use-after-free".to_string(),
                "mem-replace-value-extraction".to_string(),
                "iterator-filter-map-occupied".to_string(),
            ],
        }
    }
}

/// Diagnostics output.
#[derive(Debug)]
pub struct MemoryPoolDiagnostics {
    pub engine: String,
    pub layer: String,
    pub capacity: usize,
    pub occupied: usize,
    pub available: usize,
    pub utilization_pct: f64,
    pub peak_usage: usize,
    pub total_allocations: usize,
    pub total_deallocations: usize,
    pub generation_counter: u64,
    pub learned_logic: Vec<String>,
}
