// moe_trtllm_pressure_monitor.rs — System Layer: Rust GPU Pressure Monitor
// Memory-safe daemon monitoring VRAM pressure for TensorRT-LLM scheduler.

use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

pub struct VramPressureMonitor {
    total_vram: usize,
    used_vram: Arc<AtomicUsize>,
    pressure_threshold: f32,
}

impl VramPressureMonitor {
    pub fn new(total_vram_mb: usize, threshold: f32) -> Self {
        Self {
            total_vram: total_vram_mb,
            used_vram: Arc::new(AtomicUsize::new(0)),
            pressure_threshold: threshold,
        }
    }

    pub fn update_usage(&self, current_usage_mb: usize) {
        self.used_vram.store(current_usage_mb, Ordering::Release);
    }

    pub fn get_pressure_ratio(&self) -> f32 {
        let used = self.used_vram.load(Ordering::Acquire) as f32;
        used / (self.total_vram as f32)
    }

    pub fn requires_eviction(&self) -> bool {
        self.get_pressure_ratio() >= self.pressure_threshold
    }

    pub fn get_available_vram(&self) -> usize {
        let used = self.used_vram.load(Ordering::Acquire);
        if self.total_vram > used {
            self.total_vram - used
        } else {
            0
        }
    }
}
