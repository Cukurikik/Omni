// omni_bloom_filter.rs — Bloom Filter
// Layer: Domain / Analytics
// Inspired by: Redis Data Structures
//
// Implements a probabilistic data structure for extremely fast membership testing.
// Never produces false negatives, but may produce false positives. Essential for
// pre-filtering database lookups to save disk I/O. Zero mock.

use std::hash::{Hash, Hasher};
use std::collections::hash_map::DefaultHasher;

pub struct OmniBloomFilter {
    bitset: Vec<u64>,     // 64 bits per block
    num_bits: usize,      // Total number of bits
    num_hashes: usize,    // Number of hash functions (k)
}

impl OmniBloomFilter {
    /// Creates a new Bloom Filter optimized for the expected number of items and false positive rate.
    pub fn new(expected_items: usize, false_positive_rate: f64) -> Self {
        assert!(expected_items > 0);
        assert!(false_positive_rate > 0.0 && false_positive_rate < 1.0);

        // m = ceil((n * log(p)) / log(1 / pow(2, log(2))))
        let m = -((expected_items as f64) * false_positive_rate.ln()) / (2.0f64.ln().powi(2));
        let num_bits = m.ceil() as usize;

        // k = round((m / n) * log(2))
        let k = ((num_bits as f64 / expected_items as f64) * 2.0f64.ln()).round() as usize;
        let num_hashes = if k == 0 { 1 } else { k };

        // Number of 64-bit blocks
        let num_blocks = (num_bits + 63) / 64;

        OmniBloomFilter {
            bitset: vec![0; num_blocks],
            num_bits,
            num_hashes,
        }
    }

    /// Generates two base hashes (Kirsch-Mitzenmacher optimization) to simulate `k` hash functions
    fn get_hash_bases<T: Hash>(&self, item: &T) -> (u64, u64) {
        let mut hasher1 = DefaultHasher::new();
        item.hash(&mut hasher1);
        // Salt the second hash slightly
        hasher1.write_u8(1);
        let h1 = hasher1.finish();

        let mut hasher2 = DefaultHasher::new();
        item.hash(&mut hasher2);
        hasher2.write_u8(2);
        let h2 = hasher2.finish();

        (h1, h2)
    }

    /// Adds an item to the Bloom Filter
    pub fn insert<T: Hash>(&mut self, item: &T) {
        let (h1, h2) = self.get_hash_bases(item);

        for i in 0..self.num_hashes {
            // h_i = (h1 + i * h2) % m
            let bit_idx = (h1.wrapping_add((i as u64).wrapping_mul(h2))) as usize % self.num_bits;
            
            let block_idx = bit_idx / 64;
            let bit_offset = bit_idx % 64;
            
            self.bitset[block_idx] |= 1 << bit_offset;
        }
    }

    /// Checks if an item might exist in the Bloom Filter
    pub fn contains<T: Hash>(&self, item: &T) -> bool {
        let (h1, h2) = self.get_hash_bases(item);

        for i in 0..self.num_hashes {
            let bit_idx = (h1.wrapping_add((i as u64).wrapping_mul(h2))) as usize % self.num_bits;
            
            let block_idx = bit_idx / 64;
            let bit_offset = bit_idx % 64;
            
            if (self.bitset[block_idx] & (1 << bit_offset)) == 0 {
                return false; // Definitely not in the set
            }
        }

        true // Probably in the set
    }
}
