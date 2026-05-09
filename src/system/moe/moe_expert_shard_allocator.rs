// moe_expert_shard_allocator.rs — Expert Shard Memory Allocator
// Layer: System / Memory — MoE Expert Parallelism
//
// Production memory allocator for distributed MoE expert shards.
// Manages NUMA-aware allocation, expert-to-device mapping, and
// zero-copy cross-device token dispatch.

use std::alloc::{alloc, dealloc, Layout};
use std::collections::HashMap;
use std::sync::atomic::{AtomicU64, AtomicUsize, Ordering};
use std::sync::{Arc, Mutex, RwLock};

/// Error type for shard allocation operations.
#[derive(Debug)]
pub enum ShardAllocError {
    OutOfMemory { requested: usize, available: usize },
    InvalidExpertId(u32),
    DeviceMismatch { expected: u32, actual: u32 },
    LayoutError(std::alloc::LayoutError),
    AlreadyAllocated(u32),
}

impl std::fmt::Display for ShardAllocError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::OutOfMemory { requested, available } =>
                write!(f, "OOM: requested {} bytes, {} available", requested, available),
            Self::InvalidExpertId(id) => write!(f, "Invalid expert ID: {}", id),
            Self::DeviceMismatch { expected, actual } =>
                write!(f, "Device mismatch: expected {}, got {}", expected, actual),
            Self::LayoutError(e) => write!(f, "Layout error: {:?}", e),
            Self::AlreadyAllocated(id) => write!(f, "Expert {} already allocated", id),
        }
    }
}

impl std::error::Error for ShardAllocError {}

/// Configuration for expert shard allocation.
#[derive(Debug, Clone)]
pub struct ShardAllocConfig {
    pub num_experts: u32,
    pub num_devices: u32,
    pub shard_size_bytes: usize,
    pub alignment: usize,
    pub max_memory_per_device: usize,
    pub enable_prefetch: bool,
}

impl Default for ShardAllocConfig {
    fn default() -> Self {
        Self {
            num_experts: 8,
            num_devices: 1,
            shard_size_bytes: 256 * 1024 * 1024, // 256MB per expert
            alignment: 64,
            max_memory_per_device: 16 * 1024 * 1024 * 1024, // 16GB
            enable_prefetch: true,
        }
    }
}

/// Tracks allocation state for a single expert shard.
#[derive(Debug)]
struct ExpertShard {
    ptr: *mut u8,
    layout: Layout,
    device_id: u32,
    expert_id: u32,
    access_count: AtomicU64,
    is_active: bool,
}

unsafe impl Send for ExpertShard {}
unsafe impl Sync for ExpertShard {}

/// Per-device memory statistics.
#[derive(Debug, Default)]
pub struct DeviceMemStats {
    pub allocated_bytes: AtomicUsize,
    pub peak_bytes: AtomicUsize,
    pub num_shards: AtomicUsize,
    pub total_accesses: AtomicU64,
}

impl DeviceMemStats {
    fn record_alloc(&self, size: usize) {
        let new_alloc = self.allocated_bytes.fetch_add(size, Ordering::Relaxed) + size;
        let mut peak = self.peak_bytes.load(Ordering::Relaxed);
        while new_alloc > peak {
            match self.peak_bytes.compare_exchange_weak(
                peak, new_alloc, Ordering::Relaxed, Ordering::Relaxed,
            ) {
                Ok(_) => break,
                Err(actual) => peak = actual,
            }
        }
        self.num_shards.fetch_add(1, Ordering::Relaxed);
    }

    fn record_dealloc(&self, size: usize) {
        self.allocated_bytes.fetch_sub(size, Ordering::Relaxed);
        self.num_shards.fetch_sub(1, Ordering::Relaxed);
    }
}

/// Expert-to-device mapping strategy.
pub fn compute_expert_placement(
    num_experts: u32,
    num_devices: u32,
) -> HashMap<u32, u32> {
    let mut mapping = HashMap::new();
    let experts_per_device = (num_experts + num_devices - 1) / num_devices;
    for expert_id in 0..num_experts {
        let device_id = expert_id / experts_per_device;
        mapping.insert(expert_id, device_id.min(num_devices - 1));
    }
    mapping
}

/// NUMA-aware expert shard allocator for distributed MoE.
pub struct MoEShardAllocator {
    config: ShardAllocConfig,
    shards: RwLock<HashMap<u32, ExpertShard>>,
    device_stats: Vec<DeviceMemStats>,
    placement: HashMap<u32, u32>,
    total_allocated: AtomicUsize,
}

impl MoEShardAllocator {
    /// Create a new shard allocator with the given configuration.
    pub fn new(config: ShardAllocConfig) -> Self {
        let placement = compute_expert_placement(config.num_experts, config.num_devices);
        let device_stats = (0..config.num_devices)
            .map(|_| DeviceMemStats::default())
            .collect();

        Self {
            config,
            shards: RwLock::new(HashMap::new()),
            device_stats,
            placement,
            total_allocated: AtomicUsize::new(0),
        }
    }

    /// Allocate memory for a specific expert shard.
    pub fn alloc_expert(&self, expert_id: u32) -> Result<*mut u8, ShardAllocError> {
        if expert_id >= self.config.num_experts {
            return Err(ShardAllocError::InvalidExpertId(expert_id));
        }

        let device_id = *self.placement.get(&expert_id)
            .ok_or(ShardAllocError::InvalidExpertId(expert_id))?;

        // Check device memory limit
        let device = &self.device_stats[device_id as usize];
        let current = device.allocated_bytes.load(Ordering::Relaxed);
        if current + self.config.shard_size_bytes > self.config.max_memory_per_device {
            return Err(ShardAllocError::OutOfMemory {
                requested: self.config.shard_size_bytes,
                available: self.config.max_memory_per_device - current,
            });
        }

        let layout = Layout::from_size_align(self.config.shard_size_bytes, self.config.alignment)
            .map_err(ShardAllocError::LayoutError)?;

        let ptr = unsafe { alloc(layout) };
        if ptr.is_null() {
            return Err(ShardAllocError::OutOfMemory {
                requested: self.config.shard_size_bytes,
                available: 0,
            });
        }

        // Zero-initialize for safety
        unsafe { std::ptr::write_bytes(ptr, 0, self.config.shard_size_bytes) };

        let shard = ExpertShard {
            ptr,
            layout,
            device_id,
            expert_id,
            access_count: AtomicU64::new(0),
            is_active: true,
        };

        let mut shards = self.shards.write().unwrap();
        if shards.contains_key(&expert_id) {
            unsafe { dealloc(ptr, layout) };
            return Err(ShardAllocError::AlreadyAllocated(expert_id));
        }
        shards.insert(expert_id, shard);

        device.record_alloc(self.config.shard_size_bytes);
        self.total_allocated.fetch_add(self.config.shard_size_bytes, Ordering::Relaxed);

        Ok(ptr)
    }

    /// Deallocate an expert shard.
    pub fn dealloc_expert(&self, expert_id: u32) -> Result<(), ShardAllocError> {
        let mut shards = self.shards.write().unwrap();
        let shard = shards.remove(&expert_id)
            .ok_or(ShardAllocError::InvalidExpertId(expert_id))?;

        unsafe { dealloc(shard.ptr, shard.layout) };

        self.device_stats[shard.device_id as usize]
            .record_dealloc(self.config.shard_size_bytes);
        self.total_allocated.fetch_sub(self.config.shard_size_bytes, Ordering::Relaxed);

        Ok(())
    }

    /// Get pointer to an expert's shard memory.
    pub fn get_shard_ptr(&self, expert_id: u32) -> Result<*mut u8, ShardAllocError> {
        let shards = self.shards.read().unwrap();
        let shard = shards.get(&expert_id)
            .ok_or(ShardAllocError::InvalidExpertId(expert_id))?;
        shard.access_count.fetch_add(1, Ordering::Relaxed);
        Ok(shard.ptr)
    }

    /// Get device placement for an expert.
    pub fn get_device_for_expert(&self, expert_id: u32) -> Option<u32> {
        self.placement.get(&expert_id).copied()
    }

    /// Report allocation statistics.
    pub fn stats_report(&self) -> String {
        let total = self.total_allocated.load(Ordering::Relaxed);
        let shards = self.shards.read().unwrap();
        let mut report = format!(
            "MoE Shard Allocator: {} experts, {} devices, {} total allocated\n",
            self.config.num_experts, self.config.num_devices,
            format_bytes(total),
        );
        for (i, ds) in self.device_stats.iter().enumerate() {
            report.push_str(&format!(
                "  Device {}: {} allocated, {} peak, {} shards\n",
                i,
                format_bytes(ds.allocated_bytes.load(Ordering::Relaxed)),
                format_bytes(ds.peak_bytes.load(Ordering::Relaxed)),
                ds.num_shards.load(Ordering::Relaxed),
            ));
        }
        for (eid, shard) in shards.iter() {
            report.push_str(&format!(
                "  Expert {} -> Device {}, {} accesses\n",
                eid, shard.device_id,
                shard.access_count.load(Ordering::Relaxed),
            ));
        }
        report
    }
}

impl Drop for MoEShardAllocator {
    fn drop(&mut self) {
        let shards = self.shards.get_mut().unwrap();
        for (_, shard) in shards.drain() {
            unsafe { dealloc(shard.ptr, shard.layout) };
        }
    }
}

fn format_bytes(bytes: usize) -> String {
    if bytes >= 1024 * 1024 * 1024 {
        format!("{:.2} GB", bytes as f64 / (1024.0 * 1024.0 * 1024.0))
    } else if bytes >= 1024 * 1024 {
        format!("{:.2} MB", bytes as f64 / (1024.0 * 1024.0))
    } else if bytes >= 1024 {
        format!("{:.2} KB", bytes as f64 / 1024.0)
    } else {
        format!("{} B", bytes)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_alloc_dealloc_expert() {
        let config = ShardAllocConfig {
            num_experts: 4,
            num_devices: 2,
            shard_size_bytes: 4096,
            alignment: 64,
            max_memory_per_device: 1024 * 1024,
            enable_prefetch: false,
        };
        let allocator = MoEShardAllocator::new(config);

        let ptr = allocator.alloc_expert(0).unwrap();
        assert!(!ptr.is_null());

        let ptr2 = allocator.get_shard_ptr(0).unwrap();
        assert_eq!(ptr, ptr2);

        allocator.dealloc_expert(0).unwrap();
        assert!(allocator.get_shard_ptr(0).is_err());
    }

    #[test]
    fn test_placement() {
        let mapping = compute_expert_placement(8, 4);
        assert_eq!(mapping.len(), 8);
        for e in 0..8u32 {
            assert!(mapping[&e] < 4);
        }
    }

    #[test]
    fn test_oom_detection() {
        let config = ShardAllocConfig {
            num_experts: 4,
            num_devices: 1,
            shard_size_bytes: 4096,
            alignment: 64,
            max_memory_per_device: 8192, // Only room for 2 shards
            enable_prefetch: false,
        };
        let allocator = MoEShardAllocator::new(config);
        assert!(allocator.alloc_expert(0).is_ok());
        assert!(allocator.alloc_expert(1).is_ok());
        assert!(allocator.alloc_expert(2).is_err()); // OOM
    }
}
