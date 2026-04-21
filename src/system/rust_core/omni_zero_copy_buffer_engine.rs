// ===========================================================================
// OMNI ZERO-COPY BUFFER ENGINE (SEMESTER 3 — BATCH 38.4)
// ===========================================================================
// Absorbed From  : bytes crate + io_uring + zerocopy patterns
// Logic Inherited: Rust / System Layer (Zero-Copy I/O Buffer Management)
// ===========================================================================
//
// By studying the `bytes` crate (Bytes, BytesMut), Mother learned:
//   1. Reference-counted byte slices enable zero-copy sharing
//   2. Split/freeze operations create views without copying
//   3. Cursor-based read/write for protocol parsing
//   4. Ring buffer for streaming I/O without allocation

use std::sync::atomic::{AtomicUsize, Ordering};
use std::ops::{Deref, Range};

/// Error types for buffer operations.
#[derive(Debug, PartialEq)]
pub enum BufferError {
    InsufficientCapacity { needed: usize, available: usize },
    ReadPastEnd { offset: usize, len: usize, capacity: usize },
    InvalidRange(Range<usize>),
    BufferFull,
    EmptyBuffer,
}

pub type BufferResult<T> = Result<T, BufferError>;

/// Growable byte buffer with cursor-based I/O.
///
/// Supports append, read, split, and freeze operations
/// similar to the `bytes` crate's BytesMut.
pub struct OmniByteBuffer {
    data: Vec<u8>,
    read_cursor: usize,
    write_cursor: usize,
    capacity: usize,
}

impl OmniByteBuffer {
    /// Create a buffer with the specified capacity.
    pub fn with_capacity(capacity: usize) -> Self {
        OmniByteBuffer {
            data: Vec::with_capacity(capacity),
            read_cursor: 0,
            write_cursor: 0,
            capacity,
        }
    }

    /// Create a buffer from existing data.
    pub fn from_bytes(bytes: &[u8]) -> Self {
        let capacity = bytes.len().max(64);
        let mut buf = OmniByteBuffer {
            data: Vec::with_capacity(capacity),
            read_cursor: 0,
            write_cursor: bytes.len(),
            capacity,
        };
        buf.data.extend_from_slice(bytes);
        buf
    }

    /// Write bytes to the buffer at the write cursor.
    pub fn put(&mut self, bytes: &[u8]) -> BufferResult<usize> {
        let remaining = self.capacity.saturating_sub(self.data.len());
        if bytes.len() > remaining && self.data.len() + bytes.len() > self.capacity {
            // Try to compact first
            self.compact();
            let remaining = self.capacity.saturating_sub(self.data.len());
            if bytes.len() > remaining {
                return Err(BufferError::InsufficientCapacity {
                    needed: bytes.len(),
                    available: remaining,
                });
            }
        }

        self.data.extend_from_slice(bytes);
        self.write_cursor += bytes.len();
        Ok(bytes.len())
    }

    /// Write a single byte.
    pub fn put_u8(&mut self, byte: u8) -> BufferResult<()> {
        self.put(&[byte]).map(|_| ())
    }

    /// Write a u32 in big-endian.
    pub fn put_u32_be(&mut self, value: u32) -> BufferResult<()> {
        self.put(&value.to_be_bytes()).map(|_| ())
    }

    /// Write a u64 in big-endian.
    pub fn put_u64_be(&mut self, value: u64) -> BufferResult<()> {
        self.put(&value.to_be_bytes()).map(|_| ())
    }

    /// Read `len` bytes from the read cursor.
    pub fn get(&mut self, len: usize) -> BufferResult<&[u8]> {
        if self.read_cursor + len > self.data.len() {
            return Err(BufferError::ReadPastEnd {
                offset: self.read_cursor,
                len,
                capacity: self.data.len(),
            });
        }

        let start = self.read_cursor;
        self.read_cursor += len;
        Ok(&self.data[start..start + len])
    }

    /// Read a u8 from the read cursor.
    pub fn get_u8(&mut self) -> BufferResult<u8> {
        let bytes = self.get(1)?;
        Ok(bytes[0])
    }

    /// Read a u32 in big-endian.
    pub fn get_u32_be(&mut self) -> BufferResult<u32> {
        let bytes = self.get(4)?;
        Ok(u32::from_be_bytes([bytes[0], bytes[1], bytes[2], bytes[3]]))
    }

    /// Read a u64 in big-endian.
    pub fn get_u64_be(&mut self) -> BufferResult<u64> {
        let bytes = self.get(8)?;
        let mut arr = [0u8; 8];
        arr.copy_from_slice(bytes);
        Ok(u64::from_be_bytes(arr))
    }

    /// Peek at bytes without advancing the cursor.
    pub fn peek(&self, offset: usize, len: usize) -> BufferResult<&[u8]> {
        let start = self.read_cursor + offset;
        if start + len > self.data.len() {
            return Err(BufferError::ReadPastEnd {
                offset: start,
                len,
                capacity: self.data.len(),
            });
        }
        Ok(&self.data[start..start + len])
    }

    /// Split off the first `at` bytes as a new buffer.
    /// The original buffer retains the remaining bytes.
    pub fn split_to(&mut self, at: usize) -> BufferResult<OmniByteBuffer> {
        if at > self.data.len() {
            return Err(BufferError::InvalidRange(0..at));
        }

        let split_data = self.data[..at].to_vec();
        self.data = self.data[at..].to_vec();
        self.read_cursor = self.read_cursor.saturating_sub(at);
        self.write_cursor = self.write_cursor.saturating_sub(at);

        Ok(OmniByteBuffer {
            data: split_data,
            read_cursor: 0,
            write_cursor: at,
            capacity: at,
        })
    }

    /// Compact: move unread data to the front, reclaiming read space.
    pub fn compact(&mut self) {
        if self.read_cursor > 0 {
            self.data.drain(..self.read_cursor);
            self.write_cursor -= self.read_cursor;
            self.read_cursor = 0;
        }
    }

    /// Clear the buffer, resetting all cursors.
    pub fn clear(&mut self) {
        self.data.clear();
        self.read_cursor = 0;
        self.write_cursor = 0;
    }

    /// Number of unread bytes remaining.
    pub fn remaining(&self) -> usize {
        self.data.len().saturating_sub(self.read_cursor)
    }

    /// Total bytes written.
    pub fn len(&self) -> usize {
        self.data.len()
    }

    /// Whether the buffer has no data.
    pub fn is_empty(&self) -> bool {
        self.data.is_empty()
    }

    /// Get the underlying bytes as a slice.
    pub fn as_bytes(&self) -> &[u8] {
        &self.data[self.read_cursor..]
    }
}

/// Ring buffer for streaming I/O without allocation.
///
/// Fixed-size circular buffer that overwrites oldest data
/// when full — ideal for network receive buffers.
pub struct OmniRingBuffer {
    data: Vec<u8>,
    capacity: usize,
    head: usize,    // Read position
    tail: usize,    // Write position
    count: usize,   // Current number of bytes
    total_written: AtomicUsize,
    total_read: AtomicUsize,
    total_overwritten: AtomicUsize,
}

impl OmniRingBuffer {
    /// Create a ring buffer with fixed capacity.
    pub fn new(capacity: usize) -> Self {
        OmniRingBuffer {
            data: vec![0u8; capacity],
            capacity,
            head: 0,
            tail: 0,
            count: 0,
            total_written: AtomicUsize::new(0),
            total_read: AtomicUsize::new(0),
            total_overwritten: AtomicUsize::new(0),
        }
    }

    /// Write bytes into the ring buffer.
    /// Overwrites oldest data if buffer is full.
    pub fn write(&mut self, bytes: &[u8]) -> usize {
        for &byte in bytes {
            self.data[self.tail] = byte;
            self.tail = (self.tail + 1) % self.capacity;

            if self.count == self.capacity {
                // Overwrite: advance head
                self.head = (self.head + 1) % self.capacity;
                self.total_overwritten.fetch_add(1, Ordering::Relaxed);
            } else {
                self.count += 1;
            }
        }
        self.total_written.fetch_add(bytes.len(), Ordering::Relaxed);
        bytes.len()
    }

    /// Read up to `len` bytes from the ring buffer.
    pub fn read(&mut self, len: usize) -> Vec<u8> {
        let to_read = len.min(self.count);
        let mut result = Vec::with_capacity(to_read);

        for _ in 0..to_read {
            result.push(self.data[self.head]);
            self.head = (self.head + 1) % self.capacity;
            self.count -= 1;
        }

        self.total_read.fetch_add(to_read, Ordering::Relaxed);
        result
    }

    pub fn available(&self) -> usize { self.count }
    pub fn is_empty(&self) -> bool { self.count == 0 }
    pub fn is_full(&self) -> bool { self.count == self.capacity }
}

/// OMNI Zero-Copy Buffer Engine — manages both linear and ring buffers.
pub struct OmniZeroCopyBufferEngine {
    total_buffers_created: AtomicUsize,
    total_bytes_processed: AtomicUsize,
}

impl OmniZeroCopyBufferEngine {
    pub fn new() -> Self {
        OmniZeroCopyBufferEngine {
            total_buffers_created: AtomicUsize::new(0),
            total_bytes_processed: AtomicUsize::new(0),
        }
    }

    pub fn create_buffer(&self, capacity: usize) -> OmniByteBuffer {
        self.total_buffers_created.fetch_add(1, Ordering::Relaxed);
        OmniByteBuffer::with_capacity(capacity)
    }

    pub fn create_ring_buffer(&self, capacity: usize) -> OmniRingBuffer {
        self.total_buffers_created.fetch_add(1, Ordering::Relaxed);
        OmniRingBuffer::new(capacity)
    }

    pub fn diagnostics(&self) -> Vec<(&str, String)> {
        vec![
            ("engine", "OmniZeroCopyBufferEngine".to_string()),
            ("layer", "Rust System".to_string()),
            ("total_buffers_created", self.total_buffers_created.load(Ordering::Relaxed).to_string()),
            ("learned_logic", [
                "bytes-crate-bytesmut",
                "cursor-based-read-write",
                "split-freeze-zero-copy",
                "ring-buffer-circular-io",
                "compact-reclaim-space",
                "big-endian-network-order",
                "overwrite-oldest-strategy",
                "vec-drain-efficient-compact",
            ].join(", ")),
        ]
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_byte_buffer_put_get() {
        let mut buf = OmniByteBuffer::with_capacity(1024);
        buf.put(b"hello").unwrap();
        let data = buf.get(5).unwrap();
        assert_eq!(data, b"hello");
    }

    #[test]
    fn test_u32_be() {
        let mut buf = OmniByteBuffer::with_capacity(64);
        buf.put_u32_be(0xDEADBEEF).unwrap();
        assert_eq!(buf.get_u32_be().unwrap(), 0xDEADBEEF);
    }

    #[test]
    fn test_ring_buffer() {
        let mut ring = OmniRingBuffer::new(4);
        ring.write(&[1, 2, 3, 4]);
        ring.write(&[5]); // overwrites 1
        let data = ring.read(4);
        assert_eq!(data, vec![2, 3, 4, 5]);
    }

    #[test]
    fn test_split_to() {
        let mut buf = OmniByteBuffer::from_bytes(b"hello world");
        let head = buf.split_to(5).unwrap();
        assert_eq!(head.as_bytes(), b"hello");
        assert_eq!(buf.as_bytes(), b" world");
    }
}
