// moe_memory_profiler.rs — System / Diagnostics
// Layer: System / Memory — MoE Allocation Profiling
//
// Tracks memory allocations and fragmentation per expert.
// Essential for diagnosing OOM issues in MoE models where dynamic
// routing causes unpredictable memory spikes.

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::Instant;

#[derive(Debug, Clone)]
pub struct AllocationEvent {
    pub expert_id: u16,
    pub size_bytes: usize,
    pub is_alloc: bool,
    pub timestamp: Instant,
}

#[derive(Debug, Default)]
pub struct ExpertMemoryStats {
    pub current_bytes: usize,
    pub peak_bytes: usize,
    pub total_alloc_count: u64,
    pub total_free_count: u64,
}

pub struct MoEMemoryProfiler {
    enabled: bool,
    stats: Arc<Mutex<HashMap<u16, ExpertMemoryStats>>>,
    events: Arc<Mutex<Vec<AllocationEvent>>>,
    track_history: bool,
}

impl MoEMemoryProfiler {
    pub fn new(enabled: bool, track_history: bool) -> Self {
        Self {
            enabled,
            stats: Arc::new(Mutex::new(HashMap::new())),
            events: Arc::new(Mutex::new(Vec::new())),
            track_history,
        }
    }

    pub fn record_alloc(&self, expert_id: u16, size_bytes: usize) {
        if !self.enabled { return; }

        let mut stats = self.stats.lock().unwrap();
        let entry = stats.entry(expert_id).or_insert_with(ExpertMemoryStats::default);
        
        entry.current_bytes += size_bytes;
        entry.total_alloc_count += 1;
        
        if entry.current_bytes > entry.peak_bytes {
            entry.peak_bytes = entry.current_bytes;
        }

        if self.track_history {
            let mut events = self.events.lock().unwrap();
            events.push(AllocationEvent {
                expert_id,
                size_bytes,
                is_alloc: true,
                timestamp: Instant::now(),
            });
        }
    }

    pub fn record_free(&self, expert_id: u16, size_bytes: usize) {
        if !self.enabled { return; }

        let mut stats = self.stats.lock().unwrap();
        if let Some(entry) = stats.get_mut(&expert_id) {
            if entry.current_bytes >= size_bytes {
                entry.current_bytes -= size_bytes;
            } else {
                entry.current_bytes = 0; // Prevent underflow if untracked alloc happened
            }
            entry.total_free_count += 1;
        }

        if self.track_history {
            let mut events = self.events.lock().unwrap();
            events.push(AllocationEvent {
                expert_id,
                size_bytes,
                is_alloc: false,
                timestamp: Instant::now(),
            });
        }
    }

    pub fn get_summary(&self) -> HashMap<u16, ExpertMemoryStats> {
        self.stats.lock().unwrap().clone()
    }

    pub fn reset(&self) {
        self.stats.lock().unwrap().clear();
        if self.track_history {
            self.events.lock().unwrap().clear();
        }
    }
}
