// ===========================================================================
// OMNI OWNERSHIP ENGINE (SEMESTER 3 — BATCH 38.9)
// ===========================================================================
// Absorbed From  : Rust borrow checker + Arc/Mutex + Cow + Pin + lifetimes
// Logic Inherited: Rust / System Layer (Memory Safety & Ownership Model)
// ===========================================================================
//
// By studying Rust ownership, Mother learned:
//   1. Each value has exactly one owner; when owner goes out of scope, value is dropped
//   2. References (&T, &mut T) borrow without taking ownership
//   3. Arc<T> enables shared ownership across threads (atomic reference counting)
//   4. Mutex<T> provides interior mutability with lock-based synchronization
//   5. Cow<T> (Clone-on-Write) defers cloning until mutation is needed

use std::collections::HashMap;
use std::fmt;
use std::sync::{Arc, Mutex, RwLock};
use std::sync::atomic::{AtomicU64, Ordering};

// ============================================================
// PART 1: Smart Pointer Abstractions
// ============================================================

/// OmniOwned<T>: single-owner container with drop tracking.
pub struct OmniOwned<T> {
    value: T,
    created_at: std::time::Instant,
    id: u64,
}

static OWNED_COUNTER: AtomicU64 = AtomicU64::new(0);
static TOTAL_DROPS: AtomicU64 = AtomicU64::new(0);

impl<T> OmniOwned<T> {
    /// Create a new owned value.
    pub fn new(value: T) -> Self {
        let id = OWNED_COUNTER.fetch_add(1, Ordering::SeqCst);
        Self {
            value,
            created_at: std::time::Instant::now(),
            id,
        }
    }

    /// Borrow the inner value immutably.
    pub fn borrow(&self) -> &T {
        &self.value
    }

    /// Borrow the inner value mutably.
    pub fn borrow_mut(&mut self) -> &mut T {
        &mut self.value
    }

    /// Consume self and return the inner value (move out).
    pub fn into_inner(self) -> T {
        self.value
    }

    /// Get the unique ID of this owned value.
    pub fn id(&self) -> u64 {
        self.id
    }

    /// Get the age of this value.
    pub fn age(&self) -> std::time::Duration {
        self.created_at.elapsed()
    }

    /// Map the inner value, consuming self.
    pub fn map<U, F: FnOnce(T) -> U>(self, f: F) -> OmniOwned<U> {
        OmniOwned::new(f(self.value))
    }
}

impl<T> Drop for OmniOwned<T> {
    fn drop(&mut self) {
        TOTAL_DROPS.fetch_add(1, Ordering::SeqCst);
    }
}

impl<T: fmt::Debug> fmt::Debug for OmniOwned<T> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "OmniOwned(id={}, value={:?})", self.id, self.value)
    }
}

// ============================================================
// PART 2: Shared Ownership (Arc + Mutex/RwLock)
// ============================================================

/// OmniShared<T>: thread-safe shared ownership with interior mutability.
pub struct OmniShared<T> {
    inner: Arc<RwLock<T>>,
    read_count: Arc<AtomicU64>,
    write_count: Arc<AtomicU64>,
}

impl<T> OmniShared<T> {
    /// Create a new shared value.
    pub fn new(value: T) -> Self {
        Self {
            inner: Arc::new(RwLock::new(value)),
            read_count: Arc::new(AtomicU64::new(0)),
            write_count: Arc::new(AtomicU64::new(0)),
        }
    }

    /// Read the value (multiple readers allowed).
    pub fn read<R, F: FnOnce(&T) -> R>(&self, f: F) -> R {
        self.read_count.fetch_add(1, Ordering::Relaxed);
        let guard = self.inner.read().expect("RwLock poisoned on read");
        f(&*guard)
    }

    /// Write/mutate the value (exclusive access).
    pub fn write<R, F: FnOnce(&mut T) -> R>(&self, f: F) -> R {
        self.write_count.fetch_add(1, Ordering::Relaxed);
        let mut guard = self.inner.write().expect("RwLock poisoned on write");
        f(&mut *guard)
    }

    /// Clone the Arc (cheap, just increments ref count).
    pub fn share(&self) -> Self {
        Self {
            inner: Arc::clone(&self.inner),
            read_count: Arc::clone(&self.read_count),
            write_count: Arc::clone(&self.write_count),
        }
    }

    /// Number of strong references.
    pub fn ref_count(&self) -> usize {
        Arc::strong_count(&self.inner)
    }

    pub fn stats(&self) -> (u64, u64) {
        (
            self.read_count.load(Ordering::Relaxed),
            self.write_count.load(Ordering::Relaxed),
        )
    }
}

impl<T> Clone for OmniShared<T> {
    fn clone(&self) -> Self {
        self.share()
    }
}

// ============================================================
// PART 3: Clone-on-Write (Cow Pattern)
// ============================================================

/// OmniCow: defers cloning until mutation is required.
pub enum OmniCow<'a, T: Clone> {
    Borrowed(&'a T),
    Owned(T),
}

impl<'a, T: Clone> OmniCow<'a, T> {
    /// Get a reference to the value (no clone).
    pub fn as_ref(&self) -> &T {
        match self {
            OmniCow::Borrowed(r) => r,
            OmniCow::Owned(v) => v,
        }
    }

    /// Get a mutable reference, cloning if necessary.
    pub fn to_mut(&mut self) -> &mut T {
        match self {
            OmniCow::Borrowed(r) => {
                *self = OmniCow::Owned((*r).clone());
                match self {
                    OmniCow::Owned(v) => v,
                    _ => unreachable!(),
                }
            }
            OmniCow::Owned(v) => v,
        }
    }

    /// Convert to owned value (clones if borrowed).
    pub fn into_owned(self) -> T {
        match self {
            OmniCow::Borrowed(r) => r.clone(),
            OmniCow::Owned(v) => v,
        }
    }

    /// Check if currently borrowed.
    pub fn is_borrowed(&self) -> bool {
        matches!(self, OmniCow::Borrowed(_))
    }

    /// Check if currently owned.
    pub fn is_owned(&self) -> bool {
        matches!(self, OmniCow::Owned(_))
    }
}

// ============================================================
// PART 4: Memory Pool (Object Recycling)
// ============================================================

/// OmniPool<T>: object pool for reusing allocations.
pub struct OmniPool<T> {
    pool: Mutex<Vec<T>>,
    factory: Box<dyn Fn() -> T + Send + Sync>,
    max_size: usize,
    total_creates: AtomicU64,
    total_reuses: AtomicU64,
    total_returns: AtomicU64,
}

impl<T> OmniPool<T> {
    /// Create a new pool with a factory function and max size.
    pub fn new<F: Fn() -> T + Send + Sync + 'static>(max_size: usize, factory: F) -> Self {
        Self {
            pool: Mutex::new(Vec::with_capacity(max_size)),
            factory: Box::new(factory),
            max_size,
            total_creates: AtomicU64::new(0),
            total_reuses: AtomicU64::new(0),
            total_returns: AtomicU64::new(0),
        }
    }

    /// Get an object from the pool (or create new).
    pub fn get(&self) -> T {
        let mut pool = self.pool.lock().expect("Pool lock poisoned");
        if let Some(item) = pool.pop() {
            self.total_reuses.fetch_add(1, Ordering::Relaxed);
            item
        } else {
            self.total_creates.fetch_add(1, Ordering::Relaxed);
            (self.factory)()
        }
    }

    /// Return an object to the pool for reuse.
    pub fn put(&self, item: T) {
        let mut pool = self.pool.lock().expect("Pool lock poisoned");
        if pool.len() < self.max_size {
            pool.push(item);
            self.total_returns.fetch_add(1, Ordering::Relaxed);
        }
        // Drop the item if pool is full
    }

    /// Current pool size.
    pub fn available(&self) -> usize {
        self.pool.lock().expect("Pool lock poisoned").len()
    }

    pub fn stats(&self) -> HashMap<&str, u64> {
        let mut m = HashMap::new();
        m.insert("total_creates", self.total_creates.load(Ordering::Relaxed));
        m.insert("total_reuses", self.total_reuses.load(Ordering::Relaxed));
        m.insert("total_returns", self.total_returns.load(Ordering::Relaxed));
        m
    }
}

// ============================================================
// PART 5: RAII Guard Pattern
// ============================================================

/// ScopeGuard: executes a cleanup function when dropped (RAII).
pub struct ScopeGuard<F: FnOnce()> {
    callback: Option<F>,
}

impl<F: FnOnce()> ScopeGuard<F> {
    /// Create a new scope guard that executes `callback` on drop.
    pub fn new(callback: F) -> Self {
        Self {
            callback: Some(callback),
        }
    }

    /// Disarm the guard (prevent callback from running).
    pub fn disarm(&mut self) {
        self.callback = None;
    }
}

impl<F: FnOnce()> Drop for ScopeGuard<F> {
    fn drop(&mut self) {
        if let Some(cb) = self.callback.take() {
            cb();
        }
    }
}

/// Convenience: create a scope guard.
pub fn defer<F: FnOnce()>(callback: F) -> ScopeGuard<F> {
    ScopeGuard::new(callback)
}

// ============================================================
// Diagnostics
// ============================================================

pub fn diagnostics() -> HashMap<&'static str, Vec<&'static str>> {
    let mut m = HashMap::new();
    m.insert("engine", vec!["OmniOwnershipEngine"]);
    m.insert("layer", vec!["Rust System"]);
    m.insert("components", vec![
        "OmniOwned<T>", "OmniShared<T>", "OmniCow<T>",
        "OmniPool<T>", "ScopeGuard<F>",
    ]);
    m.insert("learned_logic", vec![
        "ownership-single-owner-drop",
        "borrow-immutable-mutable-refs",
        "arc-rwlock-shared-ownership",
        "cow-clone-on-write-deferred",
        "object-pool-allocation-reuse",
        "raii-scope-guard-cleanup",
        "atomic-counters-lock-free",
        "lifetime-annotation-borrow",
    ]);
    m
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_owned_lifecycle() {
        let owned = OmniOwned::new(42);
        assert_eq!(*owned.borrow(), 42);
        let inner = owned.into_inner();
        assert_eq!(inner, 42);
    }

    #[test]
    fn test_shared_read_write() {
        let shared = OmniShared::new(vec![1, 2, 3]);
        shared.write(|v| v.push(4));
        let len = shared.read(|v| v.len());
        assert_eq!(len, 4);
    }

    #[test]
    fn test_cow_deferred_clone() {
        let original = String::from("hello");
        let mut cow = OmniCow::Borrowed(&original);
        assert!(cow.is_borrowed());
        cow.to_mut().push_str(" world");
        assert!(cow.is_owned());
        assert_eq!(cow.as_ref(), "hello world");
    }

    #[test]
    fn test_pool_reuse() {
        let pool = OmniPool::new(2, || Vec::<u8>::with_capacity(1024));
        let v1 = pool.get();
        pool.put(v1);
        let _v2 = pool.get(); // Should reuse
        assert_eq!(pool.stats()["total_reuses"], 1);
    }
}
