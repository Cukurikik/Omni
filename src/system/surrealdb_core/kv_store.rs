use omni_std::result::{Result, Ok, Err};
use std::collections::HashMap;

pub struct KvStore {
    storage: HashMap<String, Vec<u8>>,
}

impl KvStore {
    pub fn new() -> Result<Self, std::io::Error> {
        Ok(KvStore { storage: HashMap::new() })
    }

    pub fn set(&mut self, key: String, value: Vec<u8>) -> Result<(), std::io::Error> {
        self.storage.insert(key, value);
        Ok(())
    }
}
