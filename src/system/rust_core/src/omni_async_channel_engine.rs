// ===========================================================================
// OMNI ASYNC CHANNEL ENGINE (POLYLINGUAL REMEDIATION — BATCH 37.7)
// ===========================================================================
// Absorbed From  : tokio::sync::mpsc + crossbeam-channel + flume
// Logic Inherited: Rust / System Layer (Bounded MPSC Async Channel)
// Domain Layer   : System (Rust Core)
// ===========================================================================
//
// By studying tokio's mpsc channel and crossbeam-channel, Mother learned
// that a bounded multi-producer single-consumer (MPSC) channel requires:
//   1. A shared ring buffer protected by Mutex (producers) + Condvar (wake)
//   2. Bounded capacity to provide backpressure
//   3. Sender cloning (multiple producers) with atomic reference counting
//   4. Graceful close: senders can drop; receiver sees Disconnected
//
// This implementation uses std::sync primitives (no async runtime needed)
// and provides blocking send/recv with timeout support.

use std::collections::VecDeque;
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::sync::{Arc, Condvar, Mutex};
use std::time::Duration;

// ---- Channel Errors ----

/// Error returned when sending fails.
#[derive(Debug, PartialEq)]
pub enum SendError<T> {
    /// Channel is full (bounded backpressure).
    Full(T),
    /// All receivers have been dropped — channel is disconnected.
    Disconnected(T),
}

/// Error returned when receiving fails.
#[derive(Debug, PartialEq)]
pub enum RecvError {
    /// No messages available (non-blocking check).
    Empty,
    /// All senders have been dropped AND buffer is empty.
    Disconnected,
    /// Timeout elapsed before a message arrived.
    Timeout,
}

// ---- Shared State ----

struct SharedState<T> {
    buffer: Mutex<VecDeque<T>>,
    capacity: usize,
    // Condvars for producer/consumer coordination
    not_empty: Condvar,  // Signaled when an item is pushed
    not_full: Condvar,   // Signaled when an item is popped
    // Lifecycle tracking
    sender_count: AtomicUsize,
    receiver_alive: AtomicBool,
    closed: AtomicBool,
    // Statistics
    total_sent: AtomicUsize,
    total_received: AtomicUsize,
    total_dropped: AtomicUsize,
}

// ---- Sender ----

/// Cloneable sender handle. Multiple threads can hold Sender clones.
pub struct Sender<T> {
    shared: Arc<SharedState<T>>,
}

impl<T> Clone for Sender<T> {
    fn clone(&self) -> Self {
        self.shared.sender_count.fetch_add(1, Ordering::SeqCst);
        Sender {
            shared: Arc::clone(&self.shared),
        }
    }
}

impl<T> Drop for Sender<T> {
    fn drop(&mut self) {
        let prev = self.shared.sender_count.fetch_sub(1, Ordering::SeqCst);
        if prev == 1 {
            // Last sender dropped — notify receiver
            self.shared.closed.store(true, Ordering::SeqCst);
            self.shared.not_empty.notify_all();
        }
    }
}

impl<T> Sender<T> {
    /// Send a message, blocking if the channel is full.
    pub fn send(&self, value: T) -> Result<(), SendError<T>> {
        if !self.shared.receiver_alive.load(Ordering::SeqCst) {
            return Err(SendError::Disconnected(value));
        }

        let mut buffer = self.shared.buffer.lock().unwrap();

        // Wait until there's room
        while buffer.len() >= self.shared.capacity {
            if !self.shared.receiver_alive.load(Ordering::SeqCst) {
                return Err(SendError::Disconnected(value));
            }
            buffer = self.shared.not_full.wait(buffer).unwrap();
        }

        buffer.push_back(value);
        self.shared.total_sent.fetch_add(1, Ordering::Relaxed);

        // Wake up waiting receiver
        self.shared.not_empty.notify_one();

        Ok(())
    }

    /// Try to send without blocking. Returns Full if no space.
    pub fn try_send(&self, value: T) -> Result<(), SendError<T>> {
        if !self.shared.receiver_alive.load(Ordering::SeqCst) {
            return Err(SendError::Disconnected(value));
        }

        let mut buffer = self.shared.buffer.lock().unwrap();

        if buffer.len() >= self.shared.capacity {
            self.shared.total_dropped.fetch_add(1, Ordering::Relaxed);
            return Err(SendError::Full(value));
        }

        buffer.push_back(value);
        self.shared.total_sent.fetch_add(1, Ordering::Relaxed);
        self.shared.not_empty.notify_one();

        Ok(())
    }

    /// Send with timeout.
    pub fn send_timeout(&self, value: T, timeout: Duration) -> Result<(), SendError<T>> {
        if !self.shared.receiver_alive.load(Ordering::SeqCst) {
            return Err(SendError::Disconnected(value));
        }

        let mut buffer = self.shared.buffer.lock().unwrap();

        if buffer.len() >= self.shared.capacity {
            let (guard, result) = self.shared.not_full
                .wait_timeout(buffer, timeout)
                .unwrap();
            buffer = guard;

            if result.timed_out() || buffer.len() >= self.shared.capacity {
                self.shared.total_dropped.fetch_add(1, Ordering::Relaxed);
                return Err(SendError::Full(value));
            }
        }

        buffer.push_back(value);
        self.shared.total_sent.fetch_add(1, Ordering::Relaxed);
        self.shared.not_empty.notify_one();

        Ok(())
    }

    /// Number of messages currently in the buffer.
    pub fn len(&self) -> usize {
        self.shared.buffer.lock().unwrap().len()
    }

    /// Check if the receiver is still alive.
    pub fn is_connected(&self) -> bool {
        self.shared.receiver_alive.load(Ordering::SeqCst)
    }
}

// ---- Receiver ----

/// Single receiver handle. Only ONE thread should own the Receiver.
pub struct Receiver<T> {
    shared: Arc<SharedState<T>>,
}

impl<T> Drop for Receiver<T> {
    fn drop(&mut self) {
        self.shared.receiver_alive.store(false, Ordering::SeqCst);
        // Wake all blocked senders
        self.shared.not_full.notify_all();
    }
}

impl<T> Receiver<T> {
    /// Receive a message, blocking until one is available.
    pub fn recv(&self) -> Result<T, RecvError> {
        let mut buffer = self.shared.buffer.lock().unwrap();

        loop {
            if let Some(value) = buffer.pop_front() {
                self.shared.total_received.fetch_add(1, Ordering::Relaxed);
                self.shared.not_full.notify_one();
                return Ok(value);
            }

            // Buffer empty — check if all senders are gone
            if self.shared.closed.load(Ordering::SeqCst) {
                return Err(RecvError::Disconnected);
            }

            // Wait for a sender to push something
            buffer = self.shared.not_empty.wait(buffer).unwrap();
        }
    }

    /// Try to receive without blocking.
    pub fn try_recv(&self) -> Result<T, RecvError> {
        let mut buffer = self.shared.buffer.lock().unwrap();

        match buffer.pop_front() {
            Some(value) => {
                self.shared.total_received.fetch_add(1, Ordering::Relaxed);
                self.shared.not_full.notify_one();
                Ok(value)
            }
            None => {
                if self.shared.closed.load(Ordering::SeqCst) {
                    Err(RecvError::Disconnected)
                } else {
                    Err(RecvError::Empty)
                }
            }
        }
    }

    /// Receive with timeout.
    pub fn recv_timeout(&self, timeout: Duration) -> Result<T, RecvError> {
        let mut buffer = self.shared.buffer.lock().unwrap();

        if let Some(value) = buffer.pop_front() {
            self.shared.total_received.fetch_add(1, Ordering::Relaxed);
            self.shared.not_full.notify_one();
            return Ok(value);
        }

        if self.shared.closed.load(Ordering::SeqCst) {
            return Err(RecvError::Disconnected);
        }

        let (guard, result) = self.shared.not_empty
            .wait_timeout(buffer, timeout)
            .unwrap();
        buffer = guard;

        if let Some(value) = buffer.pop_front() {
            self.shared.total_received.fetch_add(1, Ordering::Relaxed);
            self.shared.not_full.notify_one();
            Ok(value)
        } else if result.timed_out() {
            Err(RecvError::Timeout)
        } else if self.shared.closed.load(Ordering::SeqCst) {
            Err(RecvError::Disconnected)
        } else {
            Err(RecvError::Empty)
        }
    }

    /// Drain all available messages without blocking.
    pub fn drain(&self) -> Vec<T> {
        let mut buffer = self.shared.buffer.lock().unwrap();
        let items: Vec<T> = buffer.drain(..).collect();
        let count = items.len();
        self.shared.total_received.fetch_add(count, Ordering::Relaxed);
        if count > 0 {
            self.shared.not_full.notify_all();
        }
        items
    }

    /// Number of messages currently in the buffer.
    pub fn len(&self) -> usize {
        self.shared.buffer.lock().unwrap().len()
    }
}

// ---- Channel Constructor ----

/// Create a bounded MPSC channel with the given capacity.
/// Returns (Sender, Receiver). The Sender can be cloned for multiple producers.
pub fn channel<T>(capacity: usize) -> (Sender<T>, Receiver<T>) {
    let shared = Arc::new(SharedState {
        buffer: Mutex::new(VecDeque::with_capacity(capacity)),
        capacity,
        not_empty: Condvar::new(),
        not_full: Condvar::new(),
        sender_count: AtomicUsize::new(1),
        receiver_alive: AtomicBool::new(true),
        closed: AtomicBool::new(false),
        total_sent: AtomicUsize::new(0),
        total_received: AtomicUsize::new(0),
        total_dropped: AtomicUsize::new(0),
    });

    (
        Sender { shared: Arc::clone(&shared) },
        Receiver { shared },
    )
}

// ---- Engine Wrapper for OMNI Registry ----

/// Engine wrapper providing diagnostics interface for OMNI Engine Registry.
pub struct OmniAsyncChannelEngine {
    _marker: std::marker::PhantomData<()>,
}

impl OmniAsyncChannelEngine {
    pub fn diagnostics() -> ChannelDiagnostics {
        ChannelDiagnostics {
            engine: "OmniAsyncChannelEngine".to_string(),
            layer: "Rust System".to_string(),
            channel_type: "bounded-mpsc".to_string(),
            features: vec![
                "blocking-send-recv".to_string(),
                "try-send-recv-nonblocking".to_string(),
                "timeout-variants".to_string(),
                "sender-cloning-mpsc".to_string(),
                "condvar-producer-consumer".to_string(),
                "graceful-disconnect-detection".to_string(),
                "drain-batch-receive".to_string(),
            ],
            learned_logic: vec![
                "tokio-mpsc-channel-design".to_string(),
                "crossbeam-bounded-backpressure".to_string(),
                "condvar-not-empty-not-full".to_string(),
                "arc-atomic-refcount-sender-clone".to_string(),
                "seqcst-ordering-lifecycle".to_string(),
                "deque-ring-buffer-backing".to_string(),
            ],
        }
    }
}

#[derive(Debug)]
pub struct ChannelDiagnostics {
    pub engine: String,
    pub layer: String,
    pub channel_type: String,
    pub features: Vec<String>,
    pub learned_logic: Vec<String>,
}
