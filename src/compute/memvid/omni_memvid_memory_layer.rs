// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Memvid Memory Layer (OMNI Zero-Mock Implementation)
// Implements Least-Recently-Used (LRU) vector cache eviction logic mathematically.

use std::collections::{HashMap, VecDeque};

pub struct Result<T> {
    pub value: Option<T>,
    pub error: Option<String>,
    pub is_ok: bool,
}

impl<T> Result<T> {
    pub fn ok(val: T) -> Self {
        Result { value: Some(val), error: None, is_ok: true }
    }
    pub fn err(err: &str) -> Self {
        Result { value: None, error: Some(err.to_string()), is_ok: false }
    }
}

pub struct MemvidCache {
    capacity: usize,
    map: HashMap<String, Vec<f32>>,
    use_queue: VecDeque<String>,
}

impl MemvidCache {
    pub fn new(capacity: usize) -> Result<Self> {
        if capacity == 0 {
            return Result::err("Cache capacity must be strictly positive.");
        }
        Result::ok(Self {
            capacity,
            map: HashMap::new(),
            use_queue: VecDeque::new(),
        })
    }

    pub fn insert(&mut self, key: String, vector: Vec<f32>) -> Result<()> {
        if self.map.contains_key(&key) {
            // Update order
            self.use_queue.retain(|k| k != &key);
            self.use_queue.push_back(key.clone());
            self.map.insert(key, vector);
            return Result::ok(());
        }

        if self.map.len() >= self.capacity {
            if let Some(oldest) = self.use_queue.pop_front() {
                self.map.remove(&oldest);
            }
        }

        self.map.insert(key.clone(), vector);
        self.use_queue.push_back(key);
        Result::ok(())
    }

    pub fn get(&mut self, key: &str) -> Result<Vec<f32>> {
        if let Some(vec) = self.map.get(key) {
            let cloned = vec.clone();
            // Demote others, promote self
            self.use_queue.retain(|k| k != key);
            self.use_queue.push_back(key.to_string());
            Result::ok(cloned)
        } else {
             Result::err("Key not found in Memvid cache.")
        }
    }
}
