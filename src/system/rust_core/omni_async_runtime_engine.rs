// ===========================================================================
// OMNI ASYNC RUNTIME ENGINE (SEMESTER 3 — BATCH 38.9)
// ===========================================================================
// Absorbed From  : Tokio + async-std + smol + futures-rs
// Logic Inherited: Rust / System Layer (Async Runtime & Task Scheduling)
// ===========================================================================
//
// By studying Tokio and futures-rs, Mother learned Rust async patterns:
//   1. Future trait: poll-based lazy evaluation (no work until polled)
//   2. Runtime schedules futures across thread pool (work-stealing)
//   3. select! races multiple futures, returning first completion
//   4. JoinSet manages a dynamic set of spawned tasks
//   5. Channels (mpsc, oneshot, broadcast) for async communication

use std::collections::HashMap;
use std::future::Future;
use std::pin::Pin;
use std::sync::atomic::{AtomicU64, AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::task::{Context, Poll, Waker};
use std::time::{Duration, Instant};

// ============================================================
// PART 1: Future Combinators
// ============================================================

/// A future that resolves to a value immediately.
pub struct Ready<T> {
    value: Option<T>,
}

impl<T> Ready<T> {
    pub fn new(value: T) -> Self {
        Ready { value: Some(value) }
    }
}

impl<T: Unpin> Future for Ready<T> {
    type Output = T;

    fn poll(mut self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<Self::Output> {
        match self.value.take() {
            Some(v) => Poll::Ready(v),
            None => panic!("Ready polled after completion"),
        }
    }
}

/// A future that yields once then completes (cooperative yielding).
pub struct Yield {
    yielded: bool,
}

impl Yield {
    pub fn once() -> Self {
        Yield { yielded: false }
    }
}

impl Future for Yield {
    type Output = ();

    fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        if self.yielded {
            Poll::Ready(())
        } else {
            self.yielded = true;
            cx.waker().wake_by_ref();
            Poll::Pending
        }
    }
}

/// Map combinator: transforms the output of a future.
pub struct Map<Fut, F> {
    future: Pin<Box<Fut>>,
    f: Option<F>,
}

impl<Fut, F, T, U> Map<Fut, F>
where
    Fut: Future<Output = T>,
    F: FnOnce(T) -> U,
{
    pub fn new(future: Fut, f: F) -> Self {
        Map {
            future: Box::pin(future),
            f: Some(f),
        }
    }
}

impl<Fut, F, T, U> Future for Map<Fut, F>
where
    Fut: Future<Output = T>,
    F: FnOnce(T) -> U + Unpin,
{
    type Output = U;

    fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<U> {
        match self.future.as_mut().poll(cx) {
            Poll::Ready(val) => {
                let f = self.f.take().expect("Map polled after completion");
                Poll::Ready(f(val))
            }
            Poll::Pending => Poll::Pending,
        }
    }
}

/// AndThen combinator: chains futures (flatMap/bind).
pub struct AndThen<Fut1, Fut2, F> {
    state: AndThenState<Fut1, Fut2, F>,
}

enum AndThenState<Fut1, Fut2, F> {
    First(Pin<Box<Fut1>>, Option<F>),
    Second(Pin<Box<Fut2>>),
    Done,
}

impl<Fut1, Fut2, F, T, U> Future for AndThen<Fut1, Fut2, F>
where
    Fut1: Future<Output = T>,
    Fut2: Future<Output = U>,
    F: FnOnce(T) -> Fut2 + Unpin,
{
    type Output = U;

    fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<U> {
        loop {
            match &mut self.state {
                AndThenState::First(fut, f) => {
                    match fut.as_mut().poll(cx) {
                        Poll::Ready(val) => {
                            let f = f.take().expect("AndThen first polled after completion");
                            let next = f(val);
                            self.state = AndThenState::Second(Box::pin(next));
                        }
                        Poll::Pending => return Poll::Pending,
                    }
                }
                AndThenState::Second(fut) => {
                    match fut.as_mut().poll(cx) {
                        Poll::Ready(val) => {
                            self.state = AndThenState::Done;
                            return Poll::Ready(val);
                        }
                        Poll::Pending => return Poll::Pending,
                    }
                }
                AndThenState::Done => panic!("AndThen polled after completion"),
            }
        }
    }
}

// ============================================================
// PART 2: Async Channel (MPSC)
// ============================================================

/// Multi-producer, single-consumer async channel.
pub struct Sender<T> {
    inner: Arc<ChannelInner<T>>,
}

pub struct Receiver<T> {
    inner: Arc<ChannelInner<T>>,
}

struct ChannelInner<T> {
    buffer: Mutex<Vec<T>>,
    capacity: usize,
    closed: AtomicBool,
    waker: Mutex<Option<Waker>>,
    total_sent: AtomicU64,
    total_recv: AtomicU64,
}

/// Create a bounded async channel.
pub fn channel<T>(capacity: usize) -> (Sender<T>, Receiver<T>) {
    let inner = Arc::new(ChannelInner {
        buffer: Mutex::new(Vec::with_capacity(capacity)),
        capacity,
        closed: AtomicBool::new(false),
        waker: Mutex::new(None),
        total_sent: AtomicU64::new(0),
        total_recv: AtomicU64::new(0),
    });

    (
        Sender { inner: Arc::clone(&inner) },
        Receiver { inner },
    )
}

impl<T> Sender<T> {
    /// Send a value. Returns Err if channel is full or closed.
    pub fn send(&self, value: T) -> Result<(), T> {
        if self.inner.closed.load(Ordering::SeqCst) {
            return Err(value);
        }

        let mut buf = self.inner.buffer.lock().unwrap();
        if buf.len() >= self.inner.capacity {
            return Err(value);
        }

        buf.push(value);
        self.inner.total_sent.fetch_add(1, Ordering::Relaxed);

        // Wake the receiver
        if let Some(waker) = self.inner.waker.lock().unwrap().take() {
            waker.wake();
        }

        Ok(())
    }

    /// Close the sender side.
    pub fn close(&self) {
        self.inner.closed.store(true, Ordering::SeqCst);
    }
}

impl<T> Clone for Sender<T> {
    fn clone(&self) -> Self {
        Sender { inner: Arc::clone(&self.inner) }
    }
}

impl<T> Receiver<T> {
    /// Try to receive a value synchronously.
    pub fn try_recv(&self) -> Option<T> {
        let mut buf = self.inner.buffer.lock().unwrap();
        if buf.is_empty() {
            None
        } else {
            self.inner.total_recv.fetch_add(1, Ordering::Relaxed);
            Some(buf.remove(0))
        }
    }

    /// Check if the channel is closed and empty.
    pub fn is_closed(&self) -> bool {
        self.inner.closed.load(Ordering::SeqCst)
            && self.inner.buffer.lock().unwrap().is_empty()
    }

    pub fn stats(&self) -> (u64, u64) {
        (
            self.inner.total_sent.load(Ordering::Relaxed),
            self.inner.total_recv.load(Ordering::Relaxed),
        )
    }
}

// ============================================================
// PART 3: Task Tracker
// ============================================================

/// Tracks spawned async tasks with metrics.
pub struct TaskTracker {
    tasks: Arc<Mutex<Vec<TaskInfo>>>,
    total_spawned: AtomicU64,
    total_completed: AtomicU64,
    total_failed: AtomicU64,
}

struct TaskInfo {
    id: u64,
    name: String,
    spawned_at: Instant,
    completed: bool,
}

impl TaskTracker {
    pub fn new() -> Self {
        Self {
            tasks: Arc::new(Mutex::new(Vec::new())),
            total_spawned: AtomicU64::new(0),
            total_completed: AtomicU64::new(0),
            total_failed: AtomicU64::new(0),
        }
    }

    /// Track a new task.
    pub fn track(&self, name: &str) -> u64 {
        let id = self.total_spawned.fetch_add(1, Ordering::SeqCst);
        let mut tasks = self.tasks.lock().unwrap();
        tasks.push(TaskInfo {
            id,
            name: name.to_string(),
            spawned_at: Instant::now(),
            completed: false,
        });
        id
    }

    /// Mark a task as completed.
    pub fn complete(&self, id: u64) {
        self.total_completed.fetch_add(1, Ordering::Relaxed);
        let mut tasks = self.tasks.lock().unwrap();
        if let Some(task) = tasks.iter_mut().find(|t| t.id == id) {
            task.completed = true;
        }
    }

    /// Mark a task as failed.
    pub fn fail(&self, id: u64) {
        self.total_failed.fetch_add(1, Ordering::Relaxed);
        self.complete(id);
    }

    pub fn stats(&self) -> HashMap<&str, u64> {
        let mut m = HashMap::new();
        m.insert("total_spawned", self.total_spawned.load(Ordering::Relaxed));
        m.insert("total_completed", self.total_completed.load(Ordering::Relaxed));
        m.insert("total_failed", self.total_failed.load(Ordering::Relaxed));
        m.insert("pending", {
            let tasks = self.tasks.lock().unwrap();
            tasks.iter().filter(|t| !t.completed).count() as u64
        });
        m
    }
}

// ============================================================
// PART 4: Timeout Future
// ============================================================

/// Wraps a future with a timeout. Returns Err if the future doesn't
/// complete within the specified duration.
pub struct Timeout<Fut> {
    future: Pin<Box<Fut>>,
    deadline: Instant,
    expired: bool,
}

impl<Fut: Future> Timeout<Fut> {
    pub fn new(future: Fut, duration: Duration) -> Self {
        Self {
            future: Box::pin(future),
            deadline: Instant::now() + duration,
            expired: false,
        }
    }
}

impl<Fut: Future> Future for Timeout<Fut> {
    type Output = Result<Fut::Output, TimeoutError>;

    fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
        // Check deadline
        if Instant::now() >= self.deadline {
            return Poll::Ready(Err(TimeoutError));
        }

        // Poll inner future
        match self.future.as_mut().poll(cx) {
            Poll::Ready(val) => Poll::Ready(Ok(val)),
            Poll::Pending => {
                // Schedule wake at deadline
                cx.waker().wake_by_ref();
                Poll::Pending
            }
        }
    }
}

#[derive(Debug)]
pub struct TimeoutError;

impl std::fmt::Display for TimeoutError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "operation timed out")
    }
}

impl std::error::Error for TimeoutError {}

// ============================================================
// Diagnostics
// ============================================================

pub fn diagnostics() -> HashMap<&'static str, Vec<&'static str>> {
    let mut m = HashMap::new();
    m.insert("engine", vec!["OmniAsyncRuntimeEngine"]);
    m.insert("layer", vec!["Rust System"]);
    m.insert("components", vec![
        "Ready<T>", "Yield", "Map<Fut,F>", "AndThen<F1,F2,F>",
        "Sender<T>/Receiver<T>", "TaskTracker", "Timeout<Fut>",
    ]);
    m.insert("learned_logic", vec![
        "future-trait-poll-based",
        "pin-projection-safety",
        "map-and-then-combinators",
        "mpsc-channel-async-comm",
        "task-tracker-spawn-complete",
        "timeout-deadline-cancellation",
        "cooperative-yield-scheduling",
        "waker-notification-mechanism",
    ]);
    m
}
