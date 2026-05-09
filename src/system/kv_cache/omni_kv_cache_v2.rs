// omni_kv_cache_v2.rs — Zero-Copy KV Cache for Batch 19 Transformer Inference
// Inspired by: lucidrains/memformer memory management + SoundStorm parallel decoding
// Layer: System / Memory Management
//
// SIMD-aligned, arena-allocated key-value cache for transformer attention layers.
// Supports concurrent read/write for multi-level audio codec token caches.

use std::alloc::{alloc_zeroed, dealloc, Layout};
use std::sync::atomic::{AtomicU64, AtomicBool, Ordering};
use std::sync::Arc;
use std::ptr;

/// Cache configuration for multi-level quantizer models (SoundStorm, RQ-Transformer)
#[derive(Debug, Clone)]
pub struct MultiLevelCacheConfig {
    pub num_levels: usize,      // number of quantizer levels
    pub num_heads: usize,
    pub head_dim: usize,
    pub max_seq_len: usize,
    pub max_batch_size: usize,
    pub alignment: usize,       // SIMD alignment (64 for AVX-512)
}

impl MultiLevelCacheConfig {
    pub fn entry_floats(&self) -> usize {
        self.num_heads * self.head_dim
    }

    pub fn level_floats(&self) -> usize {
        self.max_seq_len * self.max_batch_size * self.entry_floats() * 2
    }

    pub fn total_bytes(&self) -> usize {
        self.num_levels * self.level_floats() * std::mem::size_of::<f32>()
    }
}

/// Atomic occupancy tracker for batch dimension
struct OccupancyTracker {
    positions: Vec<AtomicU64>,
    capacity: usize,
}

impl OccupancyTracker {
    fn new(batch_size: usize) -> Self {
        let positions = (0..batch_size).map(|_| AtomicU64::new(0)).collect();
        Self { positions, capacity: batch_size }
    }

    #[inline]
    fn get(&self, batch: usize) -> usize {
        self.positions[batch].load(Ordering::Acquire) as usize
    }

    #[inline]
    fn advance(&self, batch: usize) -> usize {
        (self.positions[batch].fetch_add(1, Ordering::AcqRel) + 1) as usize
    }

    #[inline]
    fn reset(&self, batch: usize) {
        self.positions[batch].store(0, Ordering::Release);
    }

    fn reset_all(&self) {
        for pos in &self.positions {
            pos.store(0, Ordering::Release);
        }
    }
}

/// Single-level KV cache backed by aligned heap allocation
pub struct LevelCache {
    key_buf: *mut f32,
    val_buf: *mut f32,
    layout: Layout,
    entry_size: usize,
    max_seq: usize,
    max_batch: usize,
    alive: AtomicBool,
}

unsafe impl Send for LevelCache {}
unsafe impl Sync for LevelCache {}

impl LevelCache {
    fn new(config: &MultiLevelCacheConfig) -> Self {
        let entry_size = config.entry_floats();
        let total_floats = config.max_seq_len * config.max_batch_size * entry_size;
        let byte_size = total_floats * std::mem::size_of::<f32>();
        let layout = Layout::from_size_align(byte_size, config.alignment)
            .expect("Invalid cache layout");

        let key_buf = unsafe { alloc_zeroed(layout) as *mut f32 };
        let val_buf = unsafe { alloc_zeroed(layout) as *mut f32 };

        assert!(!key_buf.is_null(), "Key buffer allocation failed for level cache");
        assert!(!val_buf.is_null(), "Value buffer allocation failed for level cache");

        Self {
            key_buf,
            val_buf,
            layout,
            entry_size,
            max_seq: config.max_seq_len,
            max_batch: config.max_batch_size,
            alive: AtomicBool::new(true),
        }
    }

    #[inline]
    fn offset(&self, batch: usize, seq: usize) -> usize {
        debug_assert!(batch < self.max_batch && seq < self.max_seq);
        (batch * self.max_seq + seq) * self.entry_size
    }

    pub fn write_kv(&self, batch: usize, seq: usize, key: &[f32], val: &[f32]) {
        debug_assert!(self.alive.load(Ordering::Acquire));
        debug_assert_eq!(key.len(), self.entry_size);
        debug_assert_eq!(val.len(), self.entry_size);
        let off = self.offset(batch, seq);
        unsafe {
            ptr::copy_nonoverlapping(key.as_ptr(), self.key_buf.add(off), self.entry_size);
            ptr::copy_nonoverlapping(val.as_ptr(), self.val_buf.add(off), self.entry_size);
        }
    }

    pub fn read_keys(&self, batch: usize, len: usize) -> &[f32] {
        debug_assert!(self.alive.load(Ordering::Acquire));
        let off = self.offset(batch, 0);
        unsafe { std::slice::from_raw_parts(self.key_buf.add(off), len * self.entry_size) }
    }

    pub fn read_vals(&self, batch: usize, len: usize) -> &[f32] {
        debug_assert!(self.alive.load(Ordering::Acquire));
        let off = self.offset(batch, 0);
        unsafe { std::slice::from_raw_parts(self.val_buf.add(off), len * self.entry_size) }
    }

    /// Compute dot-product attention scores between a query and cached keys
    pub fn dot_product_attention(
        &self, batch: usize, query: &[f32], seq_len: usize, scale: f32
    ) -> Vec<f32> {
        debug_assert_eq!(query.len(), self.entry_size);
        let keys = self.read_keys(batch, seq_len);
        let mut scores = Vec::with_capacity(seq_len);

        for pos in 0..seq_len {
            let key_start = pos * self.entry_size;
            let mut dot: f32 = 0.0;
            for d in 0..self.entry_size {
                dot += query[d] * keys[key_start + d];
            }
            scores.push(dot * scale);
        }

        // Softmax
        let max_score = scores.iter().cloned().fold(f32::NEG_INFINITY, f32::max);
        let exp_sum: f32 = scores.iter().map(|s| (s - max_score).exp()).sum();
        for s in scores.iter_mut() {
            *s = (*s - max_score).exp() / exp_sum;
        }
        scores
    }
}

impl Drop for LevelCache {
    fn drop(&mut self) {
        self.alive.store(false, Ordering::Release);
        unsafe {
            dealloc(self.key_buf as *mut u8, self.layout);
            dealloc(self.val_buf as *mut u8, self.layout);
        }
    }
}

/// Multi-level KV cache spanning all quantizer levels
pub struct OmniMultiLevelKVCache {
    levels: Vec<LevelCache>,
    tracker: Arc<OccupancyTracker>,
    config: MultiLevelCacheConfig,
}

impl OmniMultiLevelKVCache {
    pub fn new(config: MultiLevelCacheConfig) -> Self {
        let tracker = Arc::new(OccupancyTracker::new(config.max_batch_size));
        let levels = (0..config.num_levels)
            .map(|_| LevelCache::new(&config))
            .collect();
        Self { levels, tracker, config }
    }

    pub fn level(&self, idx: usize) -> &LevelCache {
        &self.levels[idx]
    }

    pub fn append_kv(&self, level: usize, batch: usize, key: &[f32], val: &[f32]) -> usize {
        let seq_pos = self.tracker.get(batch);
        self.levels[level].write_kv(batch, seq_pos, key, val);
        if level == 0 {
            self.tracker.advance(batch)
        } else {
            seq_pos + 1
        }
    }

    pub fn current_length(&self, batch: usize) -> usize {
        self.tracker.get(batch)
    }

    pub fn reset_batch(&self, batch: usize) {
        self.tracker.reset(batch);
    }

    pub fn reset_all(&self) {
        self.tracker.reset_all();
    }

    pub fn memory_usage_bytes(&self) -> usize {
        self.config.total_bytes()
    }

    pub fn num_levels(&self) -> usize {
        self.config.num_levels
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_multi_level_cache() {
        let config = MultiLevelCacheConfig {
            num_levels: 4,
            num_heads: 2,
            head_dim: 16,
            max_seq_len: 32,
            max_batch_size: 2,
            alignment: 64,
        };
        let cache = OmniMultiLevelKVCache::new(config);

        let entry_size = 2 * 16;
        let key: Vec<f32> = (0..entry_size).map(|i| i as f32 * 0.1).collect();
        let val: Vec<f32> = (0..entry_size).map(|i| i as f32 * 0.2).collect();

        let len = cache.append_kv(0, 0, &key, &val);
        assert_eq!(len, 1);

        let keys = cache.level(0).read_keys(0, 1);
        assert_eq!(keys.len(), entry_size);
        assert!((keys[1] - 0.1).abs() < 1e-6);
    }

    #[test]
    fn test_attention_scores() {
        let config = MultiLevelCacheConfig {
            num_levels: 1,
            num_heads: 1,
            head_dim: 4,
            max_seq_len: 8,
            max_batch_size: 1,
            alignment: 64,
        };
        let cache = OmniMultiLevelKVCache::new(config);

        let k1 = vec![1.0, 0.0, 0.0, 0.0];
        let v1 = vec![1.0, 1.0, 1.0, 1.0];
        let k2 = vec![0.0, 1.0, 0.0, 0.0];
        let v2 = vec![2.0, 2.0, 2.0, 2.0];

        cache.append_kv(0, 0, &k1, &v1);
        cache.append_kv(0, 0, &k2, &v2);

        let query = vec![1.0, 0.0, 0.0, 0.0];
        let scores = cache.level(0).dot_product_attention(0, &query, 2, 0.5);
        assert_eq!(scores.len(), 2);
        // First key should have higher attention than second
        assert!(scores[0] > scores[1]);
    }
}
