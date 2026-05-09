// omni_lsm_tree.rs — Log-Structured Merge-Tree (MemTable)
// Layer: System / Memory / Database
// Inspired by: LevelDB / RocksDB
//
// Implements the in-memory component (MemTable) of an LSM-Tree. 
// Uses a balanced binary search tree (BTreeMap) to absorb high-throughput 
// write operations before they are flushed to immutable SSTables on disk. Zero mock.

use std::collections::BTreeMap;
use std::sync::{Arc, RwLock};

pub struct OmniMemTable {
    // Stores Key -> Value. BTreeMap keeps keys sorted for easy sequential flushing
    table: BTreeMap<Vec<u8>, Vec<u8>>,
    // Tracks the current byte size of the table to trigger flushes
    current_size: usize,
    max_size: usize,
}

impl OmniMemTable {
    pub fn new(max_size: usize) -> Self {
        OmniMemTable {
            table: BTreeMap::new(),
            current_size: 0,
            max_size,
        }
    }

    /// Insert or update a Key-Value pair
    pub fn put(&mut self, key: &[u8], value: &[u8]) {
        let k = key.to_vec();
        let v = value.to_vec();
        
        let added_size = k.len() + v.len();
        
        // If key already exists, subtract its old size
        if let Some(old_val) = self.table.insert(k, v) {
            self.current_size -= old_val.len(); // old key length is same
        } else {
            self.current_size += added_size;
        }
    }

    /// Retrieve a value by key
    pub fn get(&self, key: &[u8]) -> Option<Vec<u8>> {
        self.table.get(key).cloned()
    }

    /// Mark a key as deleted (Tombstone). 
    /// Represented by an empty value vector for simplicity in this implementation.
    pub fn delete(&mut self, key: &[u8]) {
        self.put(key, &[]); // Empty slice acts as tombstone
    }

    /// Check if the MemTable has reached its capacity limit
    pub fn needs_flush(&self) -> bool {
        self.current_size >= self.max_size
    }

    /// Extracts all data for flushing and resets the table
    pub fn extract_for_flush(&mut self) -> BTreeMap<Vec<u8>, Vec<u8>> {
        self.current_size = 0;
        std::mem::replace(&mut self.table, BTreeMap::new())
    }
}

/// OmniLSMTree coordinates the active MemTable and the flushing mechanism.
pub struct OmniLSMTree {
    active: Arc<RwLock<OmniMemTable>>,
    // In a full implementation, `immutable` would be a list of MemTables 
    // waiting to be written to SSTables on disk.
    immutable: Arc<RwLock<Vec<BTreeMap<Vec<u8>, Vec<u8>>>>>,
}

impl OmniLSMTree {
    pub fn new(memtable_size: usize) -> Self {
        OmniLSMTree {
            active: Arc::new(RwLock::new(OmniMemTable::new(memtable_size))),
            immutable: Arc::new(RwLock::new(Vec::new())),
        }
    }

    pub fn put(&self, key: &[u8], value: &[u8]) {
        let mut active = self.active.write().unwrap();
        
        if active.needs_flush() {
            // Move current table to immutable list
            let flush_data = active.extract_for_flush();
            let mut imms = self.immutable.write().unwrap();
            imms.push(flush_data);
            
            // In a real system, signal a background thread to write `imms` to disk here.
        }

        active.put(key, value);
    }

    pub fn get(&self, key: &[u8]) -> Option<Vec<u8>> {
        // 1. Check active MemTable
        {
            let active = self.active.read().unwrap();
            if let Some(val) = active.get(key) {
                if val.is_empty() { return None; } // Tombstone
                return Some(val);
            }
        }

        // 2. Check immutable MemTables (newest first)
        {
            let imms = self.immutable.read().unwrap();
            for table in imms.iter().rev() {
                if let Some(val) = table.get(key) {
                    if val.is_empty() { return None; } // Tombstone
                    return Some(val.clone());
                }
            }
        }

        // 3. (Not Implemented) Check disk SSTables

        None
    }
}
