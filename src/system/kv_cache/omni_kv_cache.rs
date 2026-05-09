// @omni-layer System | @omni-lang Rust | @omni-batch 18 | @omni-semester 16
// @omni-description Rust KV-cache manager for transformer inference:
// paged attention cache with eviction policies and memory pooling.

use std::collections::{HashMap, VecDeque};

#[derive(Clone)]
pub struct KVEntry {
    pub key: Vec<f32>,
    pub value: Vec<f32>,
    pub position: usize,
    pub layer: usize,
    pub head: usize,
    pub last_accessed: u64,
}

pub struct KVPage {
    entries: Vec<KVEntry>,
    capacity: usize,
}

impl KVPage {
    pub fn new(capacity: usize) -> Self {
        Self {
            entries: Vec::with_capacity(capacity),
            capacity,
        }
    }

    pub fn is_full(&self) -> bool {
        self.entries.len() >= self.capacity
    }

    pub fn push(&mut self, entry: KVEntry) -> bool {
        if self.is_full() {
            return false;
        }
        self.entries.push(entry);
        true
    }

    pub fn get(&self, idx: usize) -> Option<&KVEntry> {
        self.entries.get(idx)
    }

    pub fn len(&self) -> usize {
        self.entries.len()
    }
}

pub struct PagedKVCache {
    pages: HashMap<(usize, usize), Vec<KVPage>>, // (layer, head) -> pages
    page_size: usize,
    max_pages_per_head: usize,
    total_entries: u64,
    evictions: u64,
    access_counter: u64,
}

impl PagedKVCache {
    pub fn new(page_size: usize, max_pages: usize) -> Self {
        Self {
            pages: HashMap::new(),
            page_size,
            max_pages_per_head: max_pages,
            total_entries: 0,
            evictions: 0,
            access_counter: 0,
        }
    }

    pub fn insert(&mut self, layer: usize, head: usize, key: Vec<f32>, value: Vec<f32>, position: usize) {
        self.access_counter += 1;
        let entry = KVEntry {
            key,
            value,
            position,
            layer,
            head,
            last_accessed: self.access_counter,
        };

        let pages = self.pages.entry((layer, head)).or_insert_with(Vec::new);

        // Try to insert in last page
        if let Some(last_page) = pages.last_mut() {
            if last_page.push(entry.clone()) {
                self.total_entries += 1;
                return;
            }
        }

        // Need a new page
        if pages.len() >= self.max_pages_per_head {
            // Evict oldest page
            pages.remove(0);
            self.evictions += 1;
        }

        let mut new_page = KVPage::new(self.page_size);
        new_page.push(entry);
        pages.push(new_page);
        self.total_entries += 1;
    }

    pub fn get_all(&mut self, layer: usize, head: usize) -> Vec<&KVEntry> {
        self.access_counter += 1;
        let mut result = Vec::new();
        if let Some(pages) = self.pages.get(&(layer, head)) {
            for page in pages {
                for i in 0..page.len() {
                    if let Some(entry) = page.get(i) {
                        result.push(entry);
                    }
                }
            }
        }
        result
    }

    pub fn clear(&mut self) {
        self.pages.clear();
        self.total_entries = 0;
    }

    pub fn stats(&self) -> (u64, u64, usize) {
        let total_pages: usize = self.pages.values().map(|p| p.len()).sum();
        (self.total_entries, self.evictions, total_pages)
    }

    pub fn memory_bytes(&self) -> usize {
        let mut total = 0;
        for pages in self.pages.values() {
            for page in pages {
                for i in 0..page.len() {
                    if let Some(entry) = page.get(i) {
                        total += (entry.key.len() + entry.value.len()) * 4;
                    }
                }
            }
        }
        total
    }
}
