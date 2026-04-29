use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use std::time::{SystemTime, UNIX_EPOCH};

/// OMNI LunarDB Multi-Model Database Engine
/// System Layer — Absorbing Kazooki123/LunarDB
/// Production-grade key-value store with multi-model document/graph primitives.

pub type Result<T, E = LunarError> = std::result::Result<T, E>;

#[derive(Debug)]
pub enum LunarError {
    KeyNotFound(String),
    StorageFull,
    SerializationFault(String),
    ConcurrencyViolation,
}

#[derive(Clone, Debug)]
pub enum LunarValue {
    Text(String),
    Integer(i64),
    Float(f64),
    Binary(Vec<u8>),
    Document(HashMap<String, LunarValue>),
}

struct StorageEntry {
    value: LunarValue,
    created_at: u64,
    ttl_ms: Option<u64>,
}

pub struct OmniLunarDbEngine {
    store: Arc<RwLock<HashMap<String, StorageEntry>>>,
    max_entries: usize,
    ops_count: std::sync::atomic::AtomicU64,
}

impl OmniLunarDbEngine {
    pub fn new(max_entries: usize) -> Self {
        OmniLunarDbEngine {
            store: Arc::new(RwLock::new(HashMap::with_capacity(max_entries))),
            max_entries,
            ops_count: std::sync::atomic::AtomicU64::new(0),
        }
    }

    fn now_ms() -> u64 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_millis() as u64
    }

    pub fn put(&self, key: &str, value: LunarValue, ttl_ms: Option<u64>) -> Result<()> {
        let mut store = self.store.write().map_err(|_| LunarError::ConcurrencyViolation)?;
        if store.len() >= self.max_entries && !store.contains_key(key) {
            return Err(LunarError::StorageFull);
        }
        store.insert(key.to_string(), StorageEntry {
            value,
            created_at: Self::now_ms(),
            ttl_ms,
        });
        self.ops_count.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
        Ok(())
    }

    pub fn get(&self, key: &str) -> Result<LunarValue> {
        let store = self.store.read().map_err(|_| LunarError::ConcurrencyViolation)?;
        match store.get(key) {
            Some(entry) => {
                if let Some(ttl) = entry.ttl_ms {
                    if Self::now_ms() - entry.created_at > ttl {
                        return Err(LunarError::KeyNotFound(format!("Key '{}' expired", key)));
                    }
                }
                self.ops_count.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
                Ok(entry.value.clone())
            }
            None => Err(LunarError::KeyNotFound(key.to_string())),
        }
    }

    pub fn delete(&self, key: &str) -> Result<bool> {
        let mut store = self.store.write().map_err(|_| LunarError::ConcurrencyViolation)?;
        self.ops_count.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
        Ok(store.remove(key).is_some())
    }

    /// Purge all expired entries mathematically
    pub fn evict_expired(&self) -> Result<usize> {
        let mut store = self.store.write().map_err(|_| LunarError::ConcurrencyViolation)?;
        let now = Self::now_ms();
        let before = store.len();
        store.retain(|_, entry| {
            match entry.ttl_ms {
                Some(ttl) => (now - entry.created_at) <= ttl,
                None => true,
            }
        });
        Ok(before - store.len())
    }

    pub fn diagnostics(&self) -> HashMap<String, String> {
        let store = self.store.read().unwrap_or_else(|e| e.into_inner());
        let mut diag = HashMap::new();
        diag.insert("engine".into(), "OmniLunarDbEngine".into());
        diag.insert("entries".into(), store.len().to_string());
        diag.insert("max_entries".into(), self.max_entries.to_string());
        diag.insert("ops".into(), self.ops_count.load(std::sync::atomic::Ordering::Relaxed).to_string());
        diag.insert("status".into(), "Operational".into());
        diag
    }
}
