// ===========================================================================
// OMNI RINGBUFFER ENGINE (POLYLINGUAL REMEDIATION — BATCH 37.6)
// ===========================================================================
// Absorbed From  : ringbuf crate + LMAX Disruptor + kernel ring buffers
// Logic Inherited: Rust / System Layer (Lock-Free SPSC Ring Buffer)
// Domain Layer   : System (Rust Core)
// ===========================================================================
//
// By studying the ringbuf crate and LMAX Disruptor, Mother learned that
// a single-producer single-consumer (SPSC) ring buffer achieves lock-free
// operation by using two atomic pointers (head/tail) with acquire/release
// memory ordering. The producer only writes to tail, the consumer only
// reads from head—no CAS needed, just atomic loads with proper ordering.
//
// This is the foundational primitive for audio/video streaming pipelines
// where one thread produces data and another thread consumes it, with
// guaranteed O(1) push/pop and zero allocation after initialization.

use std::sync::atomic::{AtomicUsize, Ordering};

/// Fixed-capacity SPSC ring buffer for zero-allocation streaming.
///
/// # Safety Contract
/// - Exactly ONE thread may call `push()` (the Producer).
/// - Exactly ONE thread may call `pop()` (the Consumer).
/// - These may be different threads — the buffer is lock-free and wait-free.
///
/// # Memory Ordering
/// - Producer uses `Release` when updating tail (publishes written data).
/// - Consumer uses `Acquire` when reading tail (sees producer's writes).
/// - Consumer uses `Release` when updating head (publishes consumed slot).
/// - Producer uses `Acquire` when reading head (sees consumer's reads).
pub struct OmniRingBufferEngine<T> {
    buffer: Vec<Option<T>>,
    capacity: usize,
    head: AtomicUsize, // Consumer reads from here
    tail: AtomicUsize, // Producer writes to here
    total_pushed: AtomicUsize,
    total_popped: AtomicUsize,
    total_dropped: AtomicUsize,
}

/// Result of a push operation.
#[derive(Debug, PartialEq)]
pub enum PushResult {
    /// Successfully pushed.
    Ok,
    /// Buffer was full — item was dropped (or overwritten, depending on mode).
    Full,
}

/// Result of a pop operation.
#[derive(Debug, PartialEq)]
pub enum PopResult<T> {
    /// Successfully popped a value.
    Ok(T),
    /// Buffer was empty.
    Empty,
}

impl<T: Default + Clone> OmniRingBufferEngine<T> {
    /// Create a new ring buffer with the given capacity.
    /// Capacity is rounded up to the next power of 2 for efficient modulo (bitmasking).
    pub fn new(min_capacity: usize) -> Self {
        let capacity = min_capacity.next_power_of_two();
        let mut buffer = Vec::with_capacity(capacity);
        for _ in 0..capacity {
            buffer.push(None);
        }

        Self {
            buffer,
            capacity,
            head: AtomicUsize::new(0),
            tail: AtomicUsize::new(0),
            total_pushed: AtomicUsize::new(0),
            total_popped: AtomicUsize::new(0),
            total_dropped: AtomicUsize::new(0),
        }
    }

    /// Attempt to push an item into the buffer.
    /// Returns `PushResult::Full` if the buffer is at capacity.
    ///
    /// # Thread Safety
    /// Only ONE thread (the Producer) may call this method.
    pub fn push(&self, item: T) -> PushResult {
        let tail = self.tail.load(Ordering::Relaxed);
        let head = self.head.load(Ordering::Acquire); // See consumer's updates

        let next_tail = self.wrap(tail + 1);

        if next_tail == head {
            // Buffer is full
            self.total_dropped.fetch_add(1, Ordering::Relaxed);
            return PushResult::Full;
        }

        // SAFETY: Only the producer writes to buffer[tail], and we've verified
        // the slot is available (not occupied by the consumer's head).
        // We use unsafe to get a mutable reference to the buffer slot.
        let slot = unsafe {
            let ptr = self.buffer.as_ptr() as *mut Option<T>;
            &mut *ptr.add(self.mask(tail))
        };
        *slot = Some(item);

        // Publish: make the written data visible to the consumer
        self.tail.store(next_tail, Ordering::Release);
        self.total_pushed.fetch_add(1, Ordering::Relaxed);

        PushResult::Ok
    }

    /// Attempt to pop an item from the buffer.
    /// Returns `PopResult::Empty` if no items are available.
    ///
    /// # Thread Safety
    /// Only ONE thread (the Consumer) may call this method.
    pub fn pop(&self) -> PopResult<T> {
        let head = self.head.load(Ordering::Relaxed);
        let tail = self.tail.load(Ordering::Acquire); // See producer's updates

        if head == tail {
            return PopResult::Empty;
        }

        // SAFETY: Only the consumer reads from buffer[head], and we've verified
        // the slot is occupied (tail has advanced past it).
        let slot = unsafe {
            let ptr = self.buffer.as_ptr() as *mut Option<T>;
            &mut *ptr.add(self.mask(head))
        };

        let item = match slot.take() {
            Some(v) => v,
            None => return PopResult::Empty,
        };

        let next_head = self.wrap(head + 1);
        // Publish: make the consumed slot visible to the producer
        self.head.store(next_head, Ordering::Release);
        self.total_popped.fetch_add(1, Ordering::Relaxed);

        PopResult::Ok(item)
    }

    /// Peek at the next item without consuming it.
    pub fn peek(&self) -> Option<&T> {
        let head = self.head.load(Ordering::Relaxed);
        let tail = self.tail.load(Ordering::Acquire);

        if head == tail {
            return None;
        }

        unsafe {
            let ptr = self.buffer.as_ptr().add(self.mask(head));
            (*ptr).as_ref()
        }
    }

    /// Number of items currently in the buffer.
    pub fn len(&self) -> usize {
        let tail = self.tail.load(Ordering::Acquire);
        let head = self.head.load(Ordering::Acquire);
        self.wrap(tail.wrapping_sub(head))
    }

    /// True if the buffer is empty.
    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    /// True if the buffer is full.
    pub fn is_full(&self) -> bool {
        let tail = self.tail.load(Ordering::Acquire);
        let head = self.head.load(Ordering::Acquire);
        self.wrap(tail + 1) == head
    }

    /// Maximum number of items the buffer can hold.
    pub fn capacity(&self) -> usize {
        self.capacity - 1 // One slot is always empty (sentinel)
    }

    /// Available space remaining.
    pub fn available(&self) -> usize {
        self.capacity() - self.len()
    }

    /// Reset the buffer (NOT thread-safe — call only when idle).
    pub fn clear(&self) {
        self.head.store(0, Ordering::Release);
        self.tail.store(0, Ordering::Release);
    }

    // ---- Statistics ----

    pub fn total_pushed(&self) -> usize {
        self.total_pushed.load(Ordering::Relaxed)
    }

    pub fn total_popped(&self) -> usize {
        self.total_popped.load(Ordering::Relaxed)
    }

    pub fn total_dropped(&self) -> usize {
        self.total_dropped.load(Ordering::Relaxed)
    }

    // ---- Internal Helpers ----

    /// Bitmask for fast modulo (works because capacity is power of 2).
    #[inline(always)]
    fn mask(&self, index: usize) -> usize {
        index & (self.capacity - 1)
    }

    /// Wrap-around for index advancement.
    #[inline(always)]
    fn wrap(&self, index: usize) -> usize {
        index & (self.capacity - 1)
    }

    // ---- Diagnostics ----

    /// Returns structured diagnostics for the OMNI Engine Registry.
    pub fn diagnostics(&self) -> RingBufferDiagnostics {
        RingBufferDiagnostics {
            engine: "OmniRingBufferEngine".to_string(),
            layer: "Rust System".to_string(),
            capacity: self.capacity(),
            current_length: self.len(),
            available_space: self.available(),
            is_empty: self.is_empty(),
            is_full: self.is_full(),
            total_pushed: self.total_pushed(),
            total_popped: self.total_popped(),
            total_dropped: self.total_dropped(),
            power_of_two_capacity: self.capacity,
            learned_logic: vec![
                "spsc-lock-free-ring-buffer".to_string(),
                "acquire-release-memory-ordering".to_string(),
                "power-of-two-bitmask-modulo".to_string(),
                "sentinel-slot-full-detection".to_string(),
                "zero-allocation-after-init".to_string(),
                "wait-free-push-pop-o1".to_string(),
            ],
        }
    }
}

/// Diagnostics output structure.
#[derive(Debug)]
pub struct RingBufferDiagnostics {
    pub engine: String,
    pub layer: String,
    pub capacity: usize,
    pub current_length: usize,
    pub available_space: usize,
    pub is_empty: bool,
    pub is_full: bool,
    pub total_pushed: usize,
    pub total_popped: usize,
    pub total_dropped: usize,
    pub power_of_two_capacity: usize,
    pub learned_logic: Vec<String>,
}

// ---- Batch Operations ----

impl<T: Default + Clone> OmniRingBufferEngine<T> {
    /// Push multiple items, returning the count of successfully pushed items.
    pub fn push_batch(&self, items: &[T]) -> usize {
        let mut count = 0;
        for item in items {
            match self.push(item.clone()) {
                PushResult::Ok => count += 1,
                PushResult::Full => break,
            }
        }
        count
    }

    /// Pop up to `max_count` items into a Vec.
    pub fn pop_batch(&self, max_count: usize) -> Vec<T> {
        let mut results = Vec::with_capacity(max_count);
        for _ in 0..max_count {
            match self.pop() {
                PopResult::Ok(item) => results.push(item),
                PopResult::Empty => break,
            }
        }
        results
    }

    /// Drain all available items.
    pub fn drain(&self) -> Vec<T> {
        self.pop_batch(self.len())
    }
}

// ---- Send + Sync (Safe for cross-thread SPSC usage) ----

unsafe impl<T: Send> Send for OmniRingBufferEngine<T> {}
unsafe impl<T: Send> Sync for OmniRingBufferEngine<T> {}
