// OMNI Divine Memory Integration: Inspired by awesome-pretrained-chinese-nlp-models
// System Layer - Rust bounded local caching registry for metadata

use std::collections::HashMap;
use std::sync::{Arc, Mutex};

pub struct OmniError {
    pub code: u32,
    pub message: String,
}

pub enum OmniResult<T> {
    Ok(T),
    Err(OmniError),
}

// Bounded capacity for Rust internal in-memory mapping cache
const MAX_CACHE_ENTRIES: usize = 2048;

pub struct NLPCacheRegistry {
    map: Arc<Mutex<HashMap<String, String>>>,
}

impl NLPCacheRegistry {
    pub fn new() -> Self {
        Self {
            map: Arc::new(Mutex::new(HashMap::with_capacity(MAX_CACHE_ENTRIES))),
        }
    }

    pub fn insert(&self, key: String, metadata: String) -> OmniResult<bool> {
        let mut map = match self.map.lock() {
            Ok(guard) => guard,
            Err(_) => return OmniResult::Err(OmniError { code: 500, message: "Mutex lock poisoned.".to_string() }),
        };

        if map.len() >= MAX_CACHE_ENTRIES {
            return OmniResult::Err(OmniError {
                code: 413,
                message: "Physical cache capacity of 2048 entries saturated.".to_string(),
            });
        }

        map.insert(key, metadata);
        OmniResult::Ok(true)
    }

    pub fn get(&self, key: &str) -> OmniResult<String> {
        let map = match self.map.lock() {
            Ok(guard) => guard,
            Err(_) => return OmniResult::Err(OmniError { code: 500, message: "Mutex lock poisoned.".to_string() }),
        };

        match map.get(key) {
            Some(val) => OmniResult::Ok(val.clone()),
            None => OmniResult::Err(OmniError { code: 404, message: "Cache key missing.".to_string() }),
        }
    }
}
