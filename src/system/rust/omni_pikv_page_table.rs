// OMNI MOTHER: PiKV Page Table Mapping
// Maps virtual sequence tokens to physical KV blocks

use std::collections::HashMap;
use std::sync::RwLock;

pub struct OmniPiKVPageTable {
    // seq_id -> list of physical blocks
    mapping: RwLock<HashMap<String, Vec<u32>>>,
}

impl OmniPiKVPageTable {
    pub fn new() -> Self {
        Self {
            mapping: RwLock::new(HashMap::new()),
        }
    }

    pub fn map_block(&self, seq_id: String, physical_block: u32) {
        let mut map = self.mapping.write().unwrap();
        map.entry(seq_id).or_insert_with(Vec::new).push(physical_block);
    }

    pub fn get_blocks(&self, seq_id: &str) -> Option<Vec<u32>> {
        let map = self.mapping.read().unwrap();
        map.get(seq_id).cloned()
    }
}
