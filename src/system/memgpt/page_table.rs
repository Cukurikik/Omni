/// OMNI MEMGPT: Virtual Page Table
/// Rust OS-like memory management structure mapping logical agent memory pages to physical disk/DB locations.
/// Source: memgpt/MemGPT

use std::collections::HashMap;

#[derive(Debug)]
pub enum PageError {
    PageFault,
    PageAlreadyExists,
}

#[derive(Clone, Debug)]
pub struct PhysicalLocation {
    pub file_offset: u64,
    pub db_id: String,
}

pub struct PageTableEntry {
    pub is_resident: bool,         // Is it in RAM (Working Memory)?
    pub physical: Option<PhysicalLocation>, // Where is it on disk/DB?
    pub last_accessed: u64,        // For LRU eviction
}

pub struct PageTable {
    entries: HashMap<u32, PageTableEntry>,
    clock: u64,
}

impl PageTable {
    pub fn new() -> Self {
        PageTable {
            entries: HashMap::new(),
            clock: 0,
        }
    }

    /// Agent requests a logical page of memory
    pub fn access_page(&mut self, logical_page: u32) -> Result<(), PageError> {
        self.clock += 1;
        
        if let Some(entry) = self.entries.get_mut(&logical_page) {
            entry.last_accessed = self.clock;
            if !entry.is_resident {
                // Emulate Page Fault (Requires fetching from DB)
                return Err(PageError::PageFault);
            }
            Ok(())
        } else {
            // Unmapped page
            Err(PageError::PageFault)
        }
    }

    /// Map a page after fetching from DB
    pub fn map_page(&mut self, logical_page: u32, phys: PhysicalLocation) {
        self.entries.insert(logical_page, PageTableEntry {
            is_resident: true,
            physical: Some(phys),
            last_accessed: self.clock,
        });
    }

    /// Find least recently used page to evict
    pub fn get_lru_page(&self) -> Option<u32> {
        let mut lru_page = None;
        let mut min_time = u64::MAX;

        for (&page, entry) in &self.entries {
            if entry.is_resident && entry.last_accessed < min_time {
                min_time = entry.last_accessed;
                lru_page = Some(page);
            }
        }
        
        lru_page
    }

    /// Evict a page from RAM
    pub fn evict_page(&mut self, logical_page: u32) {
        if let Some(entry) = self.entries.get_mut(&logical_page) {
            entry.is_resident = false;
        }
    }
}
