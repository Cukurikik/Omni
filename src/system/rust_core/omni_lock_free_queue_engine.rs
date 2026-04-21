// ===========================================================================
// OMNI LOCK-FREE QUEUE ENGINE (SEMESTER 3 — BATCH 38.4)
// ===========================================================================
// Absorbed From  : crossbeam-queue + Michael-Scott queue + tokio mpsc
// Logic Inherited: Rust / System Layer (Lock-Free MPMC Queue)
// ===========================================================================
//
// By studying crossbeam's lock-free data structures, Mother learned:
//   1. Compare-and-swap (CAS) loops replace mutex locks
//   2. Michael-Scott queue uses linked list with atomic head/tail
//   3. Epoch-based reclamation prevents ABA problem
//   4. Backoff strategy reduces contention under high load
//   5. Cache-line padding prevents false sharing

use std::sync::atomic::{AtomicPtr, AtomicUsize, Ordering};
use std::ptr;

/// Node in the lock-free linked list.
struct Node<T> {
    value: Option<T>,
    next: AtomicPtr<Node<T>>,
}

impl<T> Node<T> {
    fn new(value: T) -> *mut Self {
        Box::into_raw(Box::new(Node {
            value: Some(value),
            next: AtomicPtr::new(ptr::null_mut()),
        }))
    }

    fn sentinel() -> *mut Self {
        Box::into_raw(Box::new(Node {
            value: None,
            next: AtomicPtr::new(ptr::null_mut()),
        }))
    }
}

/// Exponential backoff for CAS retry loops.
struct Backoff {
    step: u32,
    max_step: u32,
}

impl Backoff {
    fn new() -> Self {
        Backoff { step: 0, max_step: 6 }
    }

    fn spin(&mut self) {
        let spins = 1u32 << self.step.min(self.max_step);
        for _ in 0..spins {
            std::hint::spin_loop();
        }
        self.step += 1;
    }

    fn reset(&mut self) {
        self.step = 0;
    }
}

/// Error type for queue operations.
#[derive(Debug, PartialEq)]
pub enum QueueError {
    Empty,
    Full,
    Closed,
}

pub type QueueResult<T> = Result<T, QueueError>;

/// Lock-free MPMC (Multi-Producer, Multi-Consumer) queue.
///
/// Uses the Michael-Scott algorithm with CAS-based synchronization.
/// No mutexes, no blocking — pure atomic operations.
pub struct OmniLockFreeQueueEngine<T> {
    head: AtomicPtr<Node<T>>,
    tail: AtomicPtr<Node<T>>,
    len: AtomicUsize,
    capacity: usize,

    // Metrics
    total_enqueued: AtomicUsize,
    total_dequeued: AtomicUsize,
    total_cas_retries: AtomicUsize,
    total_backoffs: AtomicUsize,
}

unsafe impl<T: Send> Send for OmniLockFreeQueueEngine<T> {}
unsafe impl<T: Send> Sync for OmniLockFreeQueueEngine<T> {}

impl<T> OmniLockFreeQueueEngine<T> {
    /// Create a new lock-free queue with bounded capacity.
    pub fn new(capacity: usize) -> Self {
        let sentinel = Node::<T>::sentinel();
        OmniLockFreeQueueEngine {
            head: AtomicPtr::new(sentinel),
            tail: AtomicPtr::new(sentinel),
            len: AtomicUsize::new(0),
            capacity,
            total_enqueued: AtomicUsize::new(0),
            total_dequeued: AtomicUsize::new(0),
            total_cas_retries: AtomicUsize::new(0),
            total_backoffs: AtomicUsize::new(0),
        }
    }

    /// Create an unbounded queue.
    pub fn unbounded() -> Self {
        Self::new(usize::MAX)
    }

    /// Enqueue a value. Returns Err(Full) if at capacity.
    ///
    /// Lock-free: uses CAS loop with exponential backoff.
    pub fn enqueue(&self, value: T) -> QueueResult<()> {
        if self.len.load(Ordering::Relaxed) >= self.capacity {
            return Err(QueueError::Full);
        }

        let new_node = Node::new(value);
        let mut backoff = Backoff::new();

        loop {
            let tail = self.tail.load(Ordering::Acquire);
            let tail_ref = unsafe { &*tail };
            let next = tail_ref.next.load(Ordering::Acquire);

            if next.is_null() {
                // Try to link new node at the tail
                match tail_ref.next.compare_exchange_weak(
                    ptr::null_mut(),
                    new_node,
                    Ordering::Release,
                    Ordering::Relaxed,
                ) {
                    Ok(_) => {
                        // Successfully linked — now swing the tail
                        let _ = self.tail.compare_exchange(
                            tail,
                            new_node,
                            Ordering::Release,
                            Ordering::Relaxed,
                        );
                        self.len.fetch_add(1, Ordering::Relaxed);
                        self.total_enqueued.fetch_add(1, Ordering::Relaxed);
                        return Ok(());
                    }
                    Err(_) => {
                        // CAS failed — another thread won, backoff and retry
                        self.total_cas_retries.fetch_add(1, Ordering::Relaxed);
                        backoff.spin();
                        self.total_backoffs.fetch_add(1, Ordering::Relaxed);
                    }
                }
            } else {
                // Tail is lagging — help advance it
                let _ = self.tail.compare_exchange(
                    tail,
                    next,
                    Ordering::Release,
                    Ordering::Relaxed,
                );
            }
        }
    }

    /// Dequeue a value. Returns Err(Empty) if queue is empty.
    ///
    /// Lock-free: uses CAS loop with exponential backoff.
    pub fn dequeue(&self) -> QueueResult<T> {
        let mut backoff = Backoff::new();

        loop {
            let head = self.head.load(Ordering::Acquire);
            let tail = self.tail.load(Ordering::Acquire);
            let head_ref = unsafe { &*head };
            let next = head_ref.next.load(Ordering::Acquire);

            if head == tail {
                if next.is_null() {
                    return Err(QueueError::Empty);
                }
                // Tail lagging — help advance
                let _ = self.tail.compare_exchange(
                    tail,
                    next,
                    Ordering::Release,
                    Ordering::Relaxed,
                );
            } else if !next.is_null() {
                // Try to swing head to next node
                let next_ref = unsafe { &mut *next };
                if let Some(value) = next_ref.value.take() {
                    match self.head.compare_exchange_weak(
                        head,
                        next,
                        Ordering::Release,
                        Ordering::Relaxed,
                    ) {
                        Ok(_) => {
                            // Successfully dequeued — free old sentinel
                            unsafe { let _ = Box::from_raw(head); }
                            self.len.fetch_sub(1, Ordering::Relaxed);
                            self.total_dequeued.fetch_add(1, Ordering::Relaxed);
                            return Ok(value);
                        }
                        Err(_) => {
                            // Put the value back (CAS failed)
                            next_ref.value = Some(value);
                            self.total_cas_retries.fetch_add(1, Ordering::Relaxed);
                            backoff.spin();
                            self.total_backoffs.fetch_add(1, Ordering::Relaxed);
                        }
                    }
                }
            }
        }
    }

    /// Current queue length (approximate under contention).
    pub fn len(&self) -> usize {
        self.len.load(Ordering::Relaxed)
    }

    /// Whether the queue is empty.
    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    /// Whether the queue is at capacity.
    pub fn is_full(&self) -> bool {
        self.len() >= self.capacity
    }

    /// OMNI Engine diagnostics.
    pub fn diagnostics(&self) -> Vec<(&str, String)> {
        vec![
            ("engine", "OmniLockFreeQueueEngine".to_string()),
            ("layer", "Rust System".to_string()),
            ("capacity", self.capacity.to_string()),
            ("current_length", self.len().to_string()),
            ("total_enqueued", self.total_enqueued.load(Ordering::Relaxed).to_string()),
            ("total_dequeued", self.total_dequeued.load(Ordering::Relaxed).to_string()),
            ("total_cas_retries", self.total_cas_retries.load(Ordering::Relaxed).to_string()),
            ("total_backoffs", self.total_backoffs.load(Ordering::Relaxed).to_string()),
            ("learned_logic", [
                "michael-scott-lock-free-queue",
                "compare-and-swap-cas-loop",
                "exponential-backoff-contention",
                "sentinel-node-technique",
                "atomic-ptr-acquire-release",
                "box-into-raw-manual-alloc",
                "spin-loop-hint-cpu",
                "help-advance-tail-cooperative",
            ].join(", ")),
        ]
    }
}

impl<T> Drop for OmniLockFreeQueueEngine<T> {
    fn drop(&mut self) {
        // Drain remaining nodes to free memory
        while self.dequeue().is_ok() {}
        // Free the sentinel
        let head = self.head.load(Ordering::Relaxed);
        if !head.is_null() {
            unsafe { let _ = Box::from_raw(head); }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_enqueue_dequeue() {
        let queue = OmniLockFreeQueueEngine::new(100);
        queue.enqueue(42).unwrap();
        queue.enqueue(99).unwrap();
        assert_eq!(queue.dequeue().unwrap(), 42);
        assert_eq!(queue.dequeue().unwrap(), 99);
        assert!(queue.is_empty());
    }

    #[test]
    fn test_empty_dequeue() {
        let queue: OmniLockFreeQueueEngine<i32> = OmniLockFreeQueueEngine::new(10);
        assert_eq!(queue.dequeue(), Err(QueueError::Empty));
    }

    #[test]
    fn test_full_enqueue() {
        let queue = OmniLockFreeQueueEngine::new(2);
        queue.enqueue(1).unwrap();
        queue.enqueue(2).unwrap();
        assert_eq!(queue.enqueue(3), Err(QueueError::Full));
    }
}
