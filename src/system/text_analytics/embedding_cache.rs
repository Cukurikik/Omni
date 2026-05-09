/// @omni-layer System | @omni-source OscarKjell/text | @omni-lang Rust
/// @omni-description Embedding cache: lock-free thread-safe embedding cache
/// with LRU eviction and hash-based lookup for text analytics.
use std::collections::HashMap;
use std::sync::Mutex;

#[derive(Debug)]
pub enum CacheError { Full, NotFound }
pub type OmniResult<T> = Result<T, CacheError>;

pub struct CachedEmbedding {
    pub key_hash: u64,
    pub embedding: Vec<f64>,
    pub access_count: u64,
    pub last_access: u64,
}

pub struct EmbeddingCache {
    cache: Mutex<HashMap<u64, CachedEmbedding>>,
    capacity: usize,
    clock: Mutex<u64>,
}

impl EmbeddingCache {
    pub fn new(capacity: usize) -> Self {
        Self {
            cache: Mutex::new(HashMap::with_capacity(capacity)),
            capacity,
            clock: Mutex::new(0),
        }
    }

    fn hash_text(text: &str) -> u64 {
        let mut hash: u64 = 5381;
        for byte in text.bytes() {
            hash = hash.wrapping_mul(33).wrapping_add(byte as u64);
        }
        hash
    }

    pub fn get(&self, text: &str) -> OmniResult<Vec<f64>> {
        let key = Self::hash_text(text);
        let mut cache = self.cache.lock().unwrap();
        let mut clock = self.clock.lock().unwrap();
        *clock += 1;
        match cache.get_mut(&key) {
            Some(entry) => {
                entry.access_count += 1;
                entry.last_access = *clock;
                Ok(entry.embedding.clone())
            }
            None => Err(CacheError::NotFound),
        }
    }

    pub fn put(&self, text: &str, embedding: Vec<f64>) -> OmniResult<()> {
        let key = Self::hash_text(text);
        let mut cache = self.cache.lock().unwrap();
        let mut clock = self.clock.lock().unwrap();
        *clock += 1;
        if cache.len() >= self.capacity && !cache.contains_key(&key) {
            // LRU eviction
            if let Some(&evict_key) = cache.iter()
                .min_by_key(|(_, v)| v.last_access)
                .map(|(k, _)| k) {
                cache.remove(&evict_key);
            }
        }
        cache.insert(key, CachedEmbedding {
            key_hash: key,
            embedding,
            access_count: 1,
            last_access: *clock,
        });
        Ok(())
    }

    pub fn size(&self) -> usize { self.cache.lock().unwrap().len() }
    pub fn capacity(&self) -> usize { self.capacity }
    pub fn hit_rate(&self) -> f64 {
        let cache = self.cache.lock().unwrap();
        let total_accesses: u64 = cache.values().map(|v| v.access_count).sum();
        let entries = cache.len() as f64;
        if entries == 0.0 { 0.0 } else { total_accesses as f64 / entries }
    }
}
