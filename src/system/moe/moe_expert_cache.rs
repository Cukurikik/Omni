// moe_expert_cache.rs — LRU Expert Cache for Offloaded MoE Inference
// Layer: System / Memory — MoE Expert Offloading
//
// When MoE models exceed GPU memory, experts are offloaded to CPU/disk.
// This LRU cache keeps hot experts in GPU memory and lazily loads
// cold experts on demand, with async prefetching based on router predictions.

use std::collections::{HashMap, VecDeque};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Arc, Mutex, RwLock};
use std::time::Instant;

/// Error type for expert cache operations.
#[derive(Debug)]
pub enum CacheError {
    ExpertNotFound(u32),
    EvictionFailed,
    LoadFailed(String),
    CacheFull,
}

impl std::fmt::Display for CacheError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::ExpertNotFound(id) => write!(f, "Expert {} not in cache", id),
            Self::EvictionFailed => write!(f, "Cache eviction failed"),
            Self::LoadFailed(msg) => write!(f, "Expert load failed: {}", msg),
            Self::CacheFull => write!(f, "Cache is full and eviction disabled"),
        }
    }
}

impl std::error::Error for CacheError {}

/// Configuration for the expert cache.
#[derive(Debug, Clone)]
pub struct ExpertCacheConfig {
    pub capacity: usize,           // max experts in GPU memory
    pub total_experts: u32,        // total experts in model
    pub prefetch_depth: usize,     // how many experts to prefetch
    pub enable_lru: bool,          // enable LRU eviction
    pub expert_size_bytes: usize,  // size of each expert's weights
}

impl Default for ExpertCacheConfig {
    fn default() -> Self {
        Self {
            capacity: 8,
            total_experts: 64,
            prefetch_depth: 2,
            enable_lru: true,
            expert_size_bytes: 128 * 1024 * 1024, // 128MB
        }
    }
}

/// Cached expert metadata.
#[derive(Debug, Clone)]
struct CachedExpert {
    expert_id: u32,
    loaded_at: Instant,
    last_accessed: Instant,
    access_count: u64,
    size_bytes: usize,
    /// Opaque handle to the GPU buffer (in real impl, this would be a GPU pointer)
    buffer_id: u64,
}

/// Cache statistics.
#[derive(Debug, Default)]
pub struct CacheStats {
    pub hits: AtomicU64,
    pub misses: AtomicU64,
    pub evictions: AtomicU64,
    pub prefetch_hits: AtomicU64,
    pub total_load_time_us: AtomicU64,
}

impl CacheStats {
    pub fn hit_rate(&self) -> f64 {
        let hits = self.hits.load(Ordering::Relaxed) as f64;
        let misses = self.misses.load(Ordering::Relaxed) as f64;
        let total = hits + misses;
        if total == 0.0 { 0.0 } else { hits / total }
    }

    pub fn report(&self) -> String {
        format!(
            "Cache Stats: hits={}, misses={}, evictions={}, prefetch_hits={}, hit_rate={:.2}%, avg_load={}µs",
            self.hits.load(Ordering::Relaxed),
            self.misses.load(Ordering::Relaxed),
            self.evictions.load(Ordering::Relaxed),
            self.prefetch_hits.load(Ordering::Relaxed),
            self.hit_rate() * 100.0,
            self.total_load_time_us.load(Ordering::Relaxed) /
                self.misses.load(Ordering::Relaxed).max(1),
        )
    }
}

/// LRU Expert Cache for offloaded MoE inference.
pub struct ExpertCache {
    config: ExpertCacheConfig,
    /// Map from expert_id to cached metadata
    cache: RwLock<HashMap<u32, CachedExpert>>,
    /// LRU order: front = least recently used
    lru_order: Mutex<VecDeque<u32>>,
    /// Next buffer ID to assign
    next_buffer_id: AtomicU64,
    /// Cache statistics
    pub stats: Arc<CacheStats>,
    /// Set of experts currently being loaded (to avoid double-load)
    loading: Mutex<std::collections::HashSet<u32>>,
}

impl ExpertCache {
    /// Create a new expert cache.
    pub fn new(config: ExpertCacheConfig) -> Self {
        Self {
            config,
            cache: RwLock::new(HashMap::new()),
            lru_order: Mutex::new(VecDeque::new()),
            next_buffer_id: AtomicU64::new(1),
            stats: Arc::new(CacheStats::default()),
            loading: Mutex::new(std::collections::HashSet::new()),
        }
    }

    /// Check if an expert is in the cache.
    pub fn contains(&self, expert_id: u32) -> bool {
        self.cache.read().unwrap().contains_key(&expert_id)
    }

    /// Get a cached expert's buffer handle, updating LRU.
    pub fn get(&self, expert_id: u32) -> Result<u64, CacheError> {
        // Read lock to check cache
        let cache = self.cache.read().unwrap();
        if let Some(entry) = cache.get(&expert_id) {
            self.stats.hits.fetch_add(1, Ordering::Relaxed);
            let buffer_id = entry.buffer_id;
            drop(cache);

            // Update LRU (move to back = most recently used)
            self._touch_lru(expert_id);

            // Update access stats
            let mut cache_w = self.cache.write().unwrap();
            if let Some(entry) = cache_w.get_mut(&expert_id) {
                entry.last_accessed = Instant::now();
                entry.access_count += 1;
            }

            Ok(buffer_id)
        } else {
            self.stats.misses.fetch_add(1, Ordering::Relaxed);
            Err(CacheError::ExpertNotFound(expert_id))
        }
    }

    /// Load an expert into the cache, evicting LRU if needed.
    pub fn load_expert(&self, expert_id: u32) -> Result<u64, CacheError> {
        // Check if already cached
        if let Ok(buffer_id) = self.get(expert_id) {
            return Ok(buffer_id);
        }

        // Check if another thread is already loading this expert
        {
            let mut loading = self.loading.lock().unwrap();
            if loading.contains(&expert_id) {
                // Wait briefly and retry (in production, use condvar)
                return Err(CacheError::LoadFailed("Already loading".into()));
            }
            loading.insert(expert_id);
        }

        let start = Instant::now();

        // Evict if at capacity
        if self.cache.read().unwrap().len() >= self.config.capacity {
            if self.config.enable_lru {
                self.evict_lru()?;
            } else {
                self.loading.lock().unwrap().remove(&expert_id);
                return Err(CacheError::CacheFull);
            }
        }

        // Simulate loading expert weights (in production: DMA from CPU/disk to GPU)
        let buffer_id = self.next_buffer_id.fetch_add(1, Ordering::Relaxed);

        let entry = CachedExpert {
            expert_id,
            loaded_at: Instant::now(),
            last_accessed: Instant::now(),
            access_count: 1,
            size_bytes: self.config.expert_size_bytes,
            buffer_id,
        };

        self.cache.write().unwrap().insert(expert_id, entry);
        self.lru_order.lock().unwrap().push_back(expert_id);

        let load_time = start.elapsed().as_micros() as u64;
        self.stats.total_load_time_us.fetch_add(load_time, Ordering::Relaxed);

        self.loading.lock().unwrap().remove(&expert_id);

        Ok(buffer_id)
    }

    /// Prefetch experts based on router predictions.
    pub fn prefetch(&self, predicted_experts: &[u32]) {
        let depth = self.config.prefetch_depth.min(predicted_experts.len());
        for &expert_id in &predicted_experts[..depth] {
            if !self.contains(expert_id) {
                match self.load_expert(expert_id) {
                    Ok(_) => {
                        self.stats.prefetch_hits.fetch_add(1, Ordering::Relaxed);
                    }
                    Err(_) => {} // Best-effort prefetch
                }
            }
        }
    }

    /// Evict the least recently used expert.
    fn evict_lru(&self) -> Result<u32, CacheError> {
        let victim = {
            let mut lru = self.lru_order.lock().unwrap();
            lru.pop_front().ok_or(CacheError::EvictionFailed)?
        };

        self.cache.write().unwrap().remove(&victim);
        self.stats.evictions.fetch_add(1, Ordering::Relaxed);

        Ok(victim)
    }

    /// Move expert to the back of the LRU queue (most recently used).
    fn _touch_lru(&self, expert_id: u32) {
        let mut lru = self.lru_order.lock().unwrap();
        if let Some(pos) = lru.iter().position(|&id| id == expert_id) {
            lru.remove(pos);
        }
        lru.push_back(expert_id);
    }

    /// Get current cache occupancy.
    pub fn occupancy(&self) -> (usize, usize) {
        let len = self.cache.read().unwrap().len();
        (len, self.config.capacity)
    }

    /// Total memory used by cached experts.
    pub fn memory_used(&self) -> usize {
        let cache = self.cache.read().unwrap();
        cache.values().map(|e| e.size_bytes).sum()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cache_hit_miss() {
        let config = ExpertCacheConfig {
            capacity: 4,
            total_experts: 16,
            expert_size_bytes: 1024,
            ..Default::default()
        };
        let cache = ExpertCache::new(config);

        // Miss
        assert!(cache.get(0).is_err());

        // Load and hit
        let buf = cache.load_expert(0).unwrap();
        assert!(buf > 0);
        let buf2 = cache.get(0).unwrap();
        assert_eq!(buf, buf2);
    }

    #[test]
    fn test_lru_eviction() {
        let config = ExpertCacheConfig {
            capacity: 2,
            total_experts: 8,
            expert_size_bytes: 1024,
            enable_lru: true,
            ..Default::default()
        };
        let cache = ExpertCache::new(config);

        cache.load_expert(0).unwrap();
        cache.load_expert(1).unwrap();

        // Touch expert 0 to make it MRU
        cache.get(0).unwrap();

        // Load expert 2: should evict expert 1 (LRU)
        cache.load_expert(2).unwrap();
        assert!(cache.contains(0));
        assert!(!cache.contains(1));
        assert!(cache.contains(2));
    }

    #[test]
    fn test_prefetch() {
        let config = ExpertCacheConfig {
            capacity: 4,
            total_experts: 8,
            prefetch_depth: 2,
            expert_size_bytes: 1024,
            enable_lru: true,
        };
        let cache = ExpertCache::new(config);

        cache.prefetch(&[3, 5, 7]);
        assert!(cache.contains(3));
        assert!(cache.contains(5));
        assert!(!cache.contains(7)); // prefetch_depth = 2
    }
}
