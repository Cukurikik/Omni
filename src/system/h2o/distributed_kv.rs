use std::collections::HashMap;
use std::sync::{Arc, RwLock};

pub struct DistributedKVStore {
    store: Arc<RwLock<HashMap<String, Vec<u8>>>>,
}

impl DistributedKVStore {
    pub fn new() -> Self {
        Self {
            store: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    pub fn put(&self, key: String, value: Vec<u8>) {
        let mut map = self.store.write().unwrap();
        map.insert(key, value);
    }

    pub fn get(&self, key: &str) -> Option<Vec<u8>> {
        let map = self.store.read().unwrap();
        map.get(key).cloned()
    }
}
