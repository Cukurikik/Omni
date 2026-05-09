// @omni-layer System | @omni-lang Rust | @omni-batch 18 | @omni-semester 16
// @omni-repo inclusionAI/asystem-awex + ServiceNow/TACTiS
// @omni-description High-performance weight shard transfer buffer: lock-free
// SPSC ring buffer for zero-copy weight shard streaming between training
// and inference processes. Inspired by AWEX shard-level transfers.

use std::sync::atomic::{AtomicU64, AtomicUsize, Ordering};
use std::alloc::{alloc, dealloc, Layout};
use std::ptr;

/// Shard transfer header stored inline in the ring buffer
#[repr(C, packed)]
#[derive(Clone, Copy)]
pub struct ShardHeader {
    pub shard_id: u64,
    pub param_hash: u64,
    pub byte_size: u32,
    pub dtype: u8,         // 0=f32, 1=f16, 2=bf16, 3=int8
    pub parallelism: u8,   // 0=DP, 1=TP, 2=PP, 3=EP
    pub src_rank: u16,
    pub checksum: u32,
}

impl ShardHeader {
    pub fn new(shard_id: u64, param_hash: u64, byte_size: u32, dtype: u8) -> Self {
        Self {
            shard_id,
            param_hash,
            byte_size,
            dtype,
            parallelism: 0,
            src_rank: 0,
            checksum: 0,
        }
    }

    pub fn compute_checksum(&mut self, data: &[u8]) {
        let mut hash: u32 = 0x811c9dc5;
        for &b in data {
            hash ^= b as u32;
            hash = hash.wrapping_mul(0x01000193);
        }
        self.checksum = hash;
    }

    pub fn verify_checksum(&self, data: &[u8]) -> bool {
        let mut hash: u32 = 0x811c9dc5;
        for &b in data {
            hash ^= b as u32;
            hash = hash.wrapping_mul(0x01000193);
        }
        hash == self.checksum
    }
}

/// Lock-free SPSC ring buffer for weight shard transfer
pub struct ShardTransferBuffer {
    buffer: *mut u8,
    capacity: usize,
    layout: Layout,
    write_pos: AtomicUsize,
    read_pos: AtomicUsize,
    shards_written: AtomicU64,
    shards_read: AtomicU64,
    bytes_transferred: AtomicU64,
}

unsafe impl Send for ShardTransferBuffer {}
unsafe impl Sync for ShardTransferBuffer {}

impl ShardTransferBuffer {
    /// Create a new transfer buffer with the given capacity (must be power of 2)
    pub fn new(capacity_bytes: usize) -> Self {
        let capacity = capacity_bytes.next_power_of_two();
        let layout = Layout::from_size_align(capacity, 64).expect("invalid layout");
        let buffer = unsafe { alloc(layout) };
        if buffer.is_null() {
            panic!("failed to allocate transfer buffer");
        }
        unsafe { ptr::write_bytes(buffer, 0, capacity) };
        Self {
            buffer,
            capacity,
            layout,
            write_pos: AtomicUsize::new(0),
            read_pos: AtomicUsize::new(0),
            shards_written: AtomicU64::new(0),
            shards_read: AtomicU64::new(0),
            bytes_transferred: AtomicU64::new(0),
        }
    }

    #[inline]
    fn mask(&self) -> usize {
        self.capacity - 1
    }

    #[inline]
    fn available_write(&self) -> usize {
        let w = self.write_pos.load(Ordering::Relaxed);
        let r = self.read_pos.load(Ordering::Acquire);
        self.capacity - (w - r)
    }

    #[inline]
    fn available_read(&self) -> usize {
        let w = self.write_pos.load(Ordering::Acquire);
        let r = self.read_pos.load(Ordering::Relaxed);
        w - r
    }

    /// Write a shard (header + data) into the buffer. Returns false if insufficient space.
    pub fn write_shard(&self, header: &ShardHeader, data: &[u8]) -> bool {
        let header_size = std::mem::size_of::<ShardHeader>();
        let total = header_size + data.len();
        let aligned_total = (total + 63) & !63; // 64-byte align

        if self.available_write() < aligned_total + 8 {
            return false;
        }

        let w = self.write_pos.load(Ordering::Relaxed);

        // Write length prefix
        let len_bytes = (aligned_total as u64).to_le_bytes();
        self.write_bytes_at(w, &len_bytes);

        // Write header
        let header_bytes = unsafe {
            std::slice::from_raw_parts(header as *const ShardHeader as *const u8, header_size)
        };
        self.write_bytes_at(w + 8, header_bytes);

        // Write data
        self.write_bytes_at(w + 8 + header_size, data);

        self.write_pos.store(w + 8 + aligned_total, Ordering::Release);
        self.shards_written.fetch_add(1, Ordering::Relaxed);
        self.bytes_transferred.fetch_add(data.len() as u64, Ordering::Relaxed);
        true
    }

    /// Read a shard from the buffer. Returns None if empty.
    pub fn read_shard(&self) -> Option<(ShardHeader, Vec<u8>)> {
        if self.available_read() < 8 {
            return None;
        }

        let r = self.read_pos.load(Ordering::Relaxed);

        // Read length prefix
        let mut len_buf = [0u8; 8];
        self.read_bytes_at(r, &mut len_buf);
        let total = u64::from_le_bytes(len_buf) as usize;

        if self.available_read() < 8 + total {
            return None;
        }

        let header_size = std::mem::size_of::<ShardHeader>();
        let mut header_bytes = vec![0u8; header_size];
        self.read_bytes_at(r + 8, &mut header_bytes);
        let header: ShardHeader = unsafe { ptr::read(header_bytes.as_ptr() as *const ShardHeader) };

        let data_size = header.byte_size as usize;
        let mut data = vec![0u8; data_size];
        self.read_bytes_at(r + 8 + header_size, &mut data);

        self.read_pos.store(r + 8 + total, Ordering::Release);
        self.shards_read.fetch_add(1, Ordering::Relaxed);

        Some((header, data))
    }

    fn write_bytes_at(&self, pos: usize, data: &[u8]) {
        for (i, &b) in data.iter().enumerate() {
            let idx = (pos + i) & self.mask();
            unsafe { *self.buffer.add(idx) = b };
        }
    }

    fn read_bytes_at(&self, pos: usize, out: &mut [u8]) {
        for (i, b) in out.iter_mut().enumerate() {
            let idx = (pos + i) & self.mask();
            *b = unsafe { *self.buffer.add(idx) };
        }
    }

    pub fn stats(&self) -> (u64, u64, u64) {
        (
            self.shards_written.load(Ordering::Relaxed),
            self.shards_read.load(Ordering::Relaxed),
            self.bytes_transferred.load(Ordering::Relaxed),
        )
    }
}

impl Drop for ShardTransferBuffer {
    fn drop(&mut self) {
        unsafe { dealloc(self.buffer, self.layout) };
    }
}
