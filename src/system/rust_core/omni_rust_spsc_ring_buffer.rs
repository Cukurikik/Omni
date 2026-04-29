// OMNI MOTHER — SEMESTER 14 BATCH 36
// Rust — System Layer (OMNI Zero-Mock Implementation)
// Implements production-grade memory-safe ring buffer for zero-copy I/O.
// Absorbs patterns from: github.com/tokio-rs/bytes, io_uring ring buffer semantics

use std::sync::atomic::{AtomicUsize, Ordering};

/// Monadic Result type for ring buffer operations.
pub type RingResult<T> = Result<T, RingBufferError>;

/// Errors specific to ring buffer operations.
#[derive(Debug, Clone)]
pub enum RingBufferError {
    /// Buffer is full — cannot write without overwriting unread data.
    BufferFull { capacity: usize, available: usize },
    /// Buffer is empty — no data to read.
    BufferEmpty,
    /// Requested size exceeds buffer capacity.
    SizeExceedsCapacity { requested: usize, capacity: usize },
    /// Invalid capacity — must be power of two.
    InvalidCapacity(usize),
}

impl std::fmt::Display for RingBufferError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::BufferFull { capacity, available } =>
                write!(f, "Ring buffer full: capacity={}, available={}", capacity, available),
            Self::BufferEmpty => write!(f, "Ring buffer empty"),
            Self::SizeExceedsCapacity { requested, capacity } =>
                write!(f, "Requested {} bytes exceeds capacity {}", requested, capacity),
            Self::InvalidCapacity(c) =>
                write!(f, "Capacity {} must be power of two", c),
        }
    }
}

impl std::error::Error for RingBufferError {}

/// Lock-free single-producer single-consumer ring buffer.
///
/// Uses power-of-two capacity with bitmask indexing for branchless wrapping.
/// Head and tail are monotonically increasing — wraparound is computed via
/// bitwise AND with `capacity - 1`, identical to Linux kernel's kfifo.
///
/// # Memory Layout
/// ```text
/// [0][1][2][3][4][5][6][7]  (capacity = 8, mask = 0b111)
///        ^tail       ^head
/// ```
pub struct RingBuffer {
    buffer: Vec<u8>,
    capacity: usize,
    mask: usize,
    head: AtomicUsize,  // Write position (producer)
    tail: AtomicUsize,  // Read position (consumer)
}

impl RingBuffer {
    /// Creates a new ring buffer with the given capacity.
    /// Capacity MUST be a power of two for branchless modular arithmetic.
    pub fn new(capacity: usize) -> RingResult<Self> {
        if capacity == 0 || (capacity & (capacity - 1)) != 0 {
            return Err(RingBufferError::InvalidCapacity(capacity));
        }

        Ok(Self {
            buffer: vec![0u8; capacity],
            capacity,
            mask: capacity - 1,
            head: AtomicUsize::new(0),
            tail: AtomicUsize::new(0),
        })
    }

    /// Returns the number of bytes available for reading.
    #[inline]
    pub fn len(&self) -> usize {
        let head = self.head.load(Ordering::Acquire);
        let tail = self.tail.load(Ordering::Acquire);
        head.wrapping_sub(tail)
    }

    /// Returns the number of bytes available for writing.
    #[inline]
    pub fn available(&self) -> usize {
        self.capacity - self.len()
    }

    /// Returns true if the buffer contains no data.
    #[inline]
    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    /// Returns true if the buffer is completely full.
    #[inline]
    pub fn is_full(&self) -> bool {
        self.len() == self.capacity
    }

    /// Writes data into the ring buffer.
    ///
    /// Returns the number of bytes actually written.
    /// Fails if there is insufficient space for the entire write.
    pub fn write(&mut self, data: &[u8]) -> RingResult<usize> {
        let available = self.available();
        if data.len() > available {
            return Err(RingBufferError::BufferFull {
                capacity: self.capacity,
                available,
            });
        }

        let head = self.head.load(Ordering::Relaxed);

        for (i, &byte) in data.iter().enumerate() {
            let idx = (head + i) & self.mask;
            self.buffer[idx] = byte;
        }

        self.head.store(head + data.len(), Ordering::Release);
        Ok(data.len())
    }

    /// Reads data from the ring buffer into the provided slice.
    ///
    /// Returns the number of bytes actually read.
    /// Fails if the buffer is empty.
    pub fn read(&mut self, out: &mut [u8]) -> RingResult<usize> {
        let readable = self.len();
        if readable == 0 {
            return Err(RingBufferError::BufferEmpty);
        }

        let to_read = out.len().min(readable);
        let tail = self.tail.load(Ordering::Relaxed);

        for i in 0..to_read {
            let idx = (tail + i) & self.mask;
            out[i] = self.buffer[idx];
        }

        self.tail.store(tail + to_read, Ordering::Release);
        Ok(to_read)
    }

    /// Returns diagnostic information about the ring buffer state.
    pub fn diagnostics(&self) -> RingBufferDiagnostics {
        RingBufferDiagnostics {
            capacity: self.capacity,
            used: self.len(),
            available: self.available(),
            head: self.head.load(Ordering::Relaxed),
            tail: self.tail.load(Ordering::Relaxed),
        }
    }
}

/// Diagnostic snapshot of ring buffer state.
#[derive(Debug)]
pub struct RingBufferDiagnostics {
    pub capacity: usize,
    pub used: usize,
    pub available: usize,
    pub head: usize,
    pub tail: usize,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_valid_capacity() {
        let rb = RingBuffer::new(1024);
        assert!(rb.is_ok());
        assert_eq!(rb.unwrap().capacity, 1024);
    }

    #[test]
    fn test_reject_non_power_of_two() {
        let rb = RingBuffer::new(100);
        assert!(rb.is_err());
    }

    #[test]
    fn test_write_read_roundtrip() {
        let mut rb = RingBuffer::new(16).unwrap();
        let data = [1u8, 2, 3, 4, 5];
        assert_eq!(rb.write(&data).unwrap(), 5);
        assert_eq!(rb.len(), 5);

        let mut out = [0u8; 5];
        assert_eq!(rb.read(&mut out).unwrap(), 5);
        assert_eq!(out, [1, 2, 3, 4, 5]);
        assert!(rb.is_empty());
    }

    #[test]
    fn test_wraparound() {
        let mut rb = RingBuffer::new(8).unwrap();
        let data = [1u8, 2, 3, 4, 5, 6];
        rb.write(&data).unwrap();

        let mut out = [0u8; 4];
        rb.read(&mut out).unwrap(); // Read 4, freeing space

        let more = [7u8, 8, 9, 10];
        rb.write(&more).unwrap(); // Should wrap around

        let mut final_out = [0u8; 6];
        assert_eq!(rb.read(&mut final_out).unwrap(), 6);
        assert_eq!(final_out, [5, 6, 7, 8, 9, 10]);
    }
}
