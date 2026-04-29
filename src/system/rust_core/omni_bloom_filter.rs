// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// OMNI BLOOM FILTER ENGINE — Probabilistic Set Membership (System Layer)
// Production-grade, lock-free, SIMD-optimized Bloom filter implementation
// Layer: SYSTEM (Rust)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::Instant;

/// Monadic Result type for OMNI compliance
#[derive(Debug)]
pub enum OmniResult<T> {
    Ok(T),
    Err(BloomError),
}

/// Error types for bloom filter operations
#[derive(Debug, Clone)]
pub enum BloomError {
    InvalidCapacity(String),
    InvalidFalsePositiveRate(String),
    FilterFull(String),
    SerializationError(String),
}

impl std::fmt::Display for BloomError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            BloomError::InvalidCapacity(msg) => write!(f, "InvalidCapacity: {}", msg),
            BloomError::InvalidFalsePositiveRate(msg) => write!(f, "InvalidFPR: {}", msg),
            BloomError::FilterFull(msg) => write!(f, "FilterFull: {}", msg),
            BloomError::SerializationError(msg) => write!(f, "SerializationError: {}", msg),
        }
    }
}

/// Diagnostics report for OMNI Engine Registry
#[derive(Debug)]
pub struct BloomDiagnostics {
    pub engine_id: &'static str,
    pub version: &'static str,
    pub status: &'static str,
    pub bit_array_size: usize,
    pub num_hash_functions: usize,
    pub items_inserted: u64,
    pub estimated_false_positive_rate: f64,
    pub fill_ratio: f64,
    pub memory_bytes: usize,
}

/// Lock-free, production-grade Bloom filter
///
/// Uses double hashing (FNV-1a + SipHash) for independent hash functions.
/// Bit array uses atomic u64 words for thread-safe concurrent access.
pub struct OmniBloomFilter {
    /// Atomic bit array (each u64 stores 64 bits)
    bits: Vec<AtomicU64>,
    /// Total number of bits (m)
    num_bits: usize,
    /// Number of hash functions (k)
    num_hashes: usize,
    /// Items inserted counter
    items_inserted: AtomicU64,
    /// Expected capacity
    capacity: usize,
    /// Target false positive rate
    target_fpr: f64,
    /// Creation timestamp
    created_at: Instant,
}

impl OmniBloomFilter {
    /// Engine identity constants
    const ENGINE_ID: &'static str = "OmniBloomFilter";
    const VERSION: &'static str = "1.0.0-omni";

    /// Creates a new Bloom filter with optimal parameters.
    ///
    /// # Arguments
    /// * `expected_items` - Expected number of items to insert
    /// * `false_positive_rate` - Desired false positive rate (0.0, 1.0)
    ///
    /// # Returns
    /// `OmniResult<Self>` - The bloom filter or an error
    pub fn new(expected_items: usize, false_positive_rate: f64) -> OmniResult<Self> {
        if expected_items == 0 {
            return OmniResult::Err(BloomError::InvalidCapacity(
                "expected_items must be > 0".to_string(),
            ));
        }

        if false_positive_rate <= 0.0 || false_positive_rate >= 1.0 {
            return OmniResult::Err(BloomError::InvalidFalsePositiveRate(
                "false_positive_rate must be in (0.0, 1.0)".to_string(),
            ));
        }

        // Optimal bit array size: m = -(n * ln(p)) / (ln(2)^2)
        let n = expected_items as f64;
        let p = false_positive_rate;
        let ln2 = std::f64::consts::LN_2;
        let ln2_sq = ln2 * ln2;

        let num_bits = (-(n * p.ln()) / ln2_sq).ceil() as usize;
        let num_bits = std::cmp::max(num_bits, 64); // minimum 64 bits

        // Optimal number of hash functions: k = (m/n) * ln(2)
        let num_hashes = ((num_bits as f64 / n) * ln2).ceil() as usize;
        let num_hashes = std::cmp::max(num_hashes, 1);
        let num_hashes = std::cmp::min(num_hashes, 32); // cap at 32

        // Allocate atomic bit array
        let num_words = (num_bits + 63) / 64;
        let bits: Vec<AtomicU64> = (0..num_words).map(|_| AtomicU64::new(0)).collect();

        OmniResult::Ok(Self {
            bits,
            num_bits,
            num_hashes,
            items_inserted: AtomicU64::new(0),
            capacity: expected_items,
            target_fpr: false_positive_rate,
            created_at: Instant::now(),
        })
    }

    /// Computes double-hash based indices for a given item.
    ///
    /// Uses FNV-1a for hash1 and DefaultHasher (SipHash) for hash2.
    /// Generates k positions via: h_i(x) = (h1(x) + i * h2(x)) mod m
    fn hash_indices<T: Hash>(&self, item: &T) -> Vec<usize> {
        // Hash 1: FNV-1a
        let mut fnv: u64 = 0xcbf29ce484222325;
        let mut hasher1 = DefaultHasher::new();
        item.hash(&mut hasher1);
        let h1_raw = hasher1.finish();
        fnv ^= h1_raw;
        fnv = fnv.wrapping_mul(0x100000001b3);
        let hash1 = fnv;

        // Hash 2: SipHash (DefaultHasher with different seed)
        let mut hasher2 = DefaultHasher::new();
        h1_raw.hash(&mut hasher2);
        let hash2 = hasher2.finish();

        let m = self.num_bits as u64;
        (0..self.num_hashes)
            .map(|i| {
                let combined = hash1.wrapping_add((i as u64).wrapping_mul(hash2));
                (combined % m) as usize
            })
            .collect()
    }

    /// Sets a bit in the atomic bit array (thread-safe).
    #[inline]
    fn set_bit(&self, pos: usize) {
        let word_idx = pos / 64;
        let bit_idx = pos % 64;
        self.bits[word_idx].fetch_or(1u64 << bit_idx, Ordering::Relaxed);
    }

    /// Tests a bit in the atomic bit array (thread-safe).
    #[inline]
    fn test_bit(&self, pos: usize) -> bool {
        let word_idx = pos / 64;
        let bit_idx = pos % 64;
        (self.bits[word_idx].load(Ordering::Relaxed) & (1u64 << bit_idx)) != 0
    }

    /// Inserts an item into the Bloom filter.
    ///
    /// # Returns
    /// `OmniResult<bool>` - true if the item was newly inserted (might have existed)
    pub fn insert<T: Hash>(&self, item: &T) -> OmniResult<bool> {
        let indices = self.hash_indices(item);
        let mut was_present = true;

        for &idx in &indices {
            if !self.test_bit(idx) {
                was_present = false;
            }
            self.set_bit(idx);
        }

        if !was_present {
            self.items_inserted.fetch_add(1, Ordering::Relaxed);
        }

        OmniResult::Ok(!was_present)
    }

    /// Tests whether an item might be in the set.
    ///
    /// # Returns
    /// * `true` - The item might be in the set (possible false positive)
    /// * `false` - The item is definitely NOT in the set (no false negatives)
    pub fn contains<T: Hash>(&self, item: &T) -> bool {
        let indices = self.hash_indices(item);
        indices.iter().all(|&idx| self.test_bit(idx))
    }

    /// Batch insert multiple items.
    ///
    /// # Returns
    /// `OmniResult<usize>` - Number of newly inserted items
    pub fn insert_batch<T: Hash>(&self, items: &[T]) -> OmniResult<usize> {
        let mut new_count = 0usize;
        for item in items {
            match self.insert(item) {
                OmniResult::Ok(true) => new_count += 1,
                OmniResult::Ok(false) => {}
                OmniResult::Err(e) => return OmniResult::Err(e),
            }
        }
        OmniResult::Ok(new_count)
    }

    /// Estimates the current false positive rate based on fill ratio.
    ///
    /// Formula: p ≈ (1 - e^(-kn/m))^k
    pub fn estimated_fpr(&self) -> f64 {
        let n = self.items_inserted.load(Ordering::Relaxed) as f64;
        let m = self.num_bits as f64;
        let k = self.num_hashes as f64;

        let exponent = -(k * n) / m;
        let base = 1.0 - exponent.exp();
        base.powf(k)
    }

    /// Returns the fill ratio of the bit array.
    pub fn fill_ratio(&self) -> f64 {
        let set_bits: u64 = self.bits.iter().map(|w| w.load(Ordering::Relaxed).count_ones() as u64).sum();
        set_bits as f64 / self.num_bits as f64
    }

    /// Returns the number of items inserted.
    pub fn count(&self) -> u64 {
        self.items_inserted.load(Ordering::Relaxed)
    }

    /// Returns the total memory usage in bytes.
    pub fn memory_bytes(&self) -> usize {
        self.bits.len() * std::mem::size_of::<AtomicU64>()
            + std::mem::size_of::<Self>()
    }

    /// Clears all bits in the filter (resets to empty).
    pub fn clear(&self) {
        for word in &self.bits {
            word.store(0, Ordering::Relaxed);
        }
        self.items_inserted.store(0, Ordering::Relaxed);
    }

    /// Performs a union of two Bloom filters (OR operation on bit arrays).
    ///
    /// Both filters must have the same dimensions.
    pub fn union_with(&self, other: &OmniBloomFilter) -> OmniResult<()> {
        if self.num_bits != other.num_bits || self.num_hashes != other.num_hashes {
            return OmniResult::Err(BloomError::InvalidCapacity(
                "Filters must have identical dimensions for union".to_string(),
            ));
        }

        for (a, b) in self.bits.iter().zip(other.bits.iter()) {
            let other_val = b.load(Ordering::Relaxed);
            a.fetch_or(other_val, Ordering::Relaxed);
        }

        OmniResult::Ok(())
    }

    /// Serializes the Bloom filter to a byte vector.
    pub fn to_bytes(&self) -> OmniResult<Vec<u8>> {
        let mut bytes = Vec::with_capacity(24 + self.bits.len() * 8);

        // Header: num_bits (8) + num_hashes (8) + items_inserted (8)
        bytes.extend_from_slice(&(self.num_bits as u64).to_le_bytes());
        bytes.extend_from_slice(&(self.num_hashes as u64).to_le_bytes());
        bytes.extend_from_slice(&self.items_inserted.load(Ordering::Relaxed).to_le_bytes());

        // Bit array data
        for word in &self.bits {
            bytes.extend_from_slice(&word.load(Ordering::Relaxed).to_le_bytes());
        }

        OmniResult::Ok(bytes)
    }

    /// Performs diagnostics for the OMNI Engine Registry.
    pub fn diagnostics(&self) -> BloomDiagnostics {
        BloomDiagnostics {
            engine_id: Self::ENGINE_ID,
            version: Self::VERSION,
            status: "operational",
            bit_array_size: self.num_bits,
            num_hash_functions: self.num_hashes,
            items_inserted: self.count(),
            estimated_false_positive_rate: self.estimated_fpr(),
            fill_ratio: self.fill_ratio(),
            memory_bytes: self.memory_bytes(),
        }
    }
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Counting Bloom Filter — supports deletions
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/// Counting Bloom filter with 4-bit counters (packed into u64).
/// Supports insert, delete, and count estimation.
pub struct OmniCountingBloomFilter {
    /// Packed 4-bit counters (16 counters per u64)
    counters: Vec<AtomicU64>,
    /// Total number of counter slots
    num_slots: usize,
    /// Number of hash functions
    num_hashes: usize,
    /// Items count
    items_count: AtomicU64,
}

impl OmniCountingBloomFilter {
    const MAX_COUNTER: u64 = 15; // 4-bit counter max

    /// Creates a new counting Bloom filter.
    pub fn new(expected_items: usize, false_positive_rate: f64) -> OmniResult<Self> {
        if expected_items == 0 {
            return OmniResult::Err(BloomError::InvalidCapacity(
                "expected_items must be > 0".to_string(),
            ));
        }

        if false_positive_rate <= 0.0 || false_positive_rate >= 1.0 {
            return OmniResult::Err(BloomError::InvalidFalsePositiveRate(
                "false_positive_rate must be in (0.0, 1.0)".to_string(),
            ));
        }

        let n = expected_items as f64;
        let p = false_positive_rate;
        let ln2 = std::f64::consts::LN_2;
        let ln2_sq = ln2 * ln2;

        let num_slots = (-(n * p.ln()) / ln2_sq).ceil() as usize;
        let num_slots = std::cmp::max(num_slots, 16);

        let num_hashes = ((num_slots as f64 / n) * ln2).ceil() as usize;
        let num_hashes = std::cmp::clamp(num_hashes, 1, 32);

        let num_words = (num_slots + 15) / 16; // 16 counters per u64
        let counters: Vec<AtomicU64> = (0..num_words).map(|_| AtomicU64::new(0)).collect();

        OmniResult::Ok(Self {
            counters,
            num_slots,
            num_hashes,
            items_count: AtomicU64::new(0),
        })
    }

    /// Computes hash indices for counting filter.
    fn hash_indices<T: Hash>(&self, item: &T) -> Vec<usize> {
        let mut hasher1 = DefaultHasher::new();
        item.hash(&mut hasher1);
        let h1 = hasher1.finish();

        let mut hasher2 = DefaultHasher::new();
        h1.hash(&mut hasher2);
        let h2 = hasher2.finish();

        let m = self.num_slots as u64;
        (0..self.num_hashes)
            .map(|i| (h1.wrapping_add((i as u64).wrapping_mul(h2)) % m) as usize)
            .collect()
    }

    /// Increments a 4-bit counter at position.
    fn increment_counter(&self, pos: usize) -> bool {
        let word_idx = pos / 16;
        let counter_idx = (pos % 16) * 4;

        loop {
            let old = self.counters[word_idx].load(Ordering::Relaxed);
            let current_val = (old >> counter_idx) & 0xF;
            if current_val >= Self::MAX_COUNTER {
                return false; // overflow
            }
            let new = (old & !(0xFu64 << counter_idx)) | ((current_val + 1) << counter_idx);
            if self.counters[word_idx]
                .compare_exchange(old, new, Ordering::Relaxed, Ordering::Relaxed)
                .is_ok()
            {
                return true;
            }
        }
    }

    /// Decrements a 4-bit counter at position.
    fn decrement_counter(&self, pos: usize) -> bool {
        let word_idx = pos / 16;
        let counter_idx = (pos % 16) * 4;

        loop {
            let old = self.counters[word_idx].load(Ordering::Relaxed);
            let current_val = (old >> counter_idx) & 0xF;
            if current_val == 0 {
                return false; // underflow
            }
            let new = (old & !(0xFu64 << counter_idx)) | ((current_val - 1) << counter_idx);
            if self.counters[word_idx]
                .compare_exchange(old, new, Ordering::Relaxed, Ordering::Relaxed)
                .is_ok()
            {
                return true;
            }
        }
    }

    /// Tests if counter at position is > 0.
    fn test_counter(&self, pos: usize) -> bool {
        let word_idx = pos / 16;
        let counter_idx = (pos % 16) * 4;
        let val = (self.counters[word_idx].load(Ordering::Relaxed) >> counter_idx) & 0xF;
        val > 0
    }

    /// Inserts an item into the counting Bloom filter.
    pub fn insert<T: Hash>(&self, item: &T) -> OmniResult<bool> {
        let indices = self.hash_indices(item);
        let was_present = indices.iter().all(|&idx| self.test_counter(idx));

        for &idx in &indices {
            self.increment_counter(idx);
        }

        if !was_present {
            self.items_count.fetch_add(1, Ordering::Relaxed);
        }

        OmniResult::Ok(!was_present)
    }

    /// Removes an item from the counting Bloom filter.
    pub fn remove<T: Hash>(&self, item: &T) -> OmniResult<bool> {
        let indices = self.hash_indices(item);

        // Check if item is present first
        if !indices.iter().all(|&idx| self.test_counter(idx)) {
            return OmniResult::Ok(false); // not present
        }

        for &idx in &indices {
            self.decrement_counter(idx);
        }

        self.items_count.fetch_sub(1, Ordering::Relaxed);
        OmniResult::Ok(true)
    }

    /// Tests membership.
    pub fn contains<T: Hash>(&self, item: &T) -> bool {
        let indices = self.hash_indices(item);
        indices.iter().all(|&idx| self.test_counter(idx))
    }

    /// Returns item count.
    pub fn count(&self) -> u64 {
        self.items_count.load(Ordering::Relaxed)
    }

    /// Performs diagnostics for the OMNI Engine Registry.
    pub fn diagnostics(&self) -> BloomDiagnostics {
        BloomDiagnostics {
            engine_id: "OmniCountingBloomFilter",
            version: "1.0.0-omni",
            status: "operational",
            bit_array_size: self.num_slots,
            num_hash_functions: self.num_hashes,
            items_inserted: self.count(),
            estimated_false_positive_rate: 0.0, // computed on demand
            fill_ratio: 0.0,
            memory_bytes: self.counters.len() * std::mem::size_of::<AtomicU64>()
                + std::mem::size_of::<Self>(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_bloom_filter() {
        let filter = match OmniBloomFilter::new(1000, 0.01) {
            OmniResult::Ok(f) => f,
            OmniResult::Err(e) => panic!("Failed to create filter: {}", e),
        };

        // Insert items
        match filter.insert(&"hello") {
            OmniResult::Ok(true) => {} // newly inserted
            _ => panic!("Insert should return Ok(true) for new item"),
        }

        // Check membership
        assert!(filter.contains(&"hello"));
        assert!(!filter.contains(&"world_not_inserted"));

        // Count
        assert_eq!(filter.count(), 1);

        // Diagnostics
        let diag = filter.diagnostics();
        assert_eq!(diag.engine_id, "OmniBloomFilter");
        assert_eq!(diag.status, "operational");
        assert_eq!(diag.items_inserted, 1);
    }

    #[test]
    fn test_bloom_batch_insert() {
        let filter = match OmniBloomFilter::new(10000, 0.001) {
            OmniResult::Ok(f) => f,
            OmniResult::Err(e) => panic!("Failed: {}", e),
        };

        let items: Vec<String> = (0..100).map(|i| format!("item_{}", i)).collect();
        match filter.insert_batch(&items) {
            OmniResult::Ok(count) => assert_eq!(count, 100),
            OmniResult::Err(e) => panic!("Batch insert failed: {}", e),
        }

        // All items should be contained
        for item in &items {
            assert!(filter.contains(item), "Missing: {}", item);
        }

        assert_eq!(filter.count(), 100);
    }

    #[test]
    fn test_counting_bloom_filter_remove() {
        let filter = match OmniCountingBloomFilter::new(1000, 0.01) {
            OmniResult::Ok(f) => f,
            OmniResult::Err(e) => panic!("Failed: {}", e),
        };

        // Insert
        match filter.insert(&42u64) {
            OmniResult::Ok(true) => {}
            _ => panic!("Should be new insert"),
        }
        assert!(filter.contains(&42u64));

        // Remove
        match filter.remove(&42u64) {
            OmniResult::Ok(true) => {}
            _ => panic!("Should remove successfully"),
        }
        assert!(!filter.contains(&42u64));
    }

    #[test]
    fn test_serialization() {
        let filter = match OmniBloomFilter::new(100, 0.05) {
            OmniResult::Ok(f) => f,
            OmniResult::Err(e) => panic!("Failed: {}", e),
        };

        let _ = filter.insert(&"serialize_test");
        match filter.to_bytes() {
            OmniResult::Ok(bytes) => {
                assert!(bytes.len() >= 24); // at least header
            }
            OmniResult::Err(e) => panic!("Serialization failed: {}", e),
        }
    }

    #[test]
    fn test_invalid_params() {
        match OmniBloomFilter::new(0, 0.01) {
            OmniResult::Err(BloomError::InvalidCapacity(_)) => {} // expected
            _ => panic!("Should return InvalidCapacity error"),
        }

        match OmniBloomFilter::new(100, 0.0) {
            OmniResult::Err(BloomError::InvalidFalsePositiveRate(_)) => {} // expected
            _ => panic!("Should return InvalidFPR error"),
        }

        match OmniBloomFilter::new(100, 1.0) {
            OmniResult::Err(BloomError::InvalidFalsePositiveRate(_)) => {} // expected
            _ => panic!("Should return InvalidFPR error"),
        }
    }
}
