// moe_xctopus_lora_manager.rs — Compute / System
// Layer: System — Dynamic LoRA Adapter Manager for Catastrophic Forgetting Prevention
// Inspired by: xctopus-core (Bayesian clustering, continual learning)

use std::collections::HashMap;
use std::sync::{Arc, RwLock};

#[derive(Clone)]
pub struct LoRAAdapter {
    pub id: String,
    pub rank: u32,
    pub alpha: f32,
    pub weight_pointer: *const u8,
    pub size_bytes: usize,
    pub bayesian_prior: f64,
}

unsafe impl Send for LoRAAdapter {}
unsafe impl Sync for LoRAAdapter {}

pub struct XctopusManager {
    adapters: RwLock<HashMap<String, Arc<LoRAAdapter>>>,
    active_capacity_bytes: usize,
}

impl XctopusManager {
    pub fn new(capacity_bytes: usize) -> Self {
        XctopusManager {
            adapters: RwLock::new(HashMap::new()),
            active_capacity_bytes: capacity_bytes,
        }
    }

    pub fn load_adapter(&self, adapter: LoRAAdapter) -> Result<(), String> {
        let mut map = self.adapters.write().map_err(|_| "Poisoned lock".to_string())?;
        
        let current_size: usize = map.values().map(|a| a.size_bytes).sum();
        if current_size + adapter.size_bytes > self.active_capacity_bytes {
            // Evict lowest Bayesian prior
            let mut lowest_id = String::new();
            let mut lowest_prior = f64::MAX;
            for (id, a) in map.iter() {
                if a.bayesian_prior < lowest_prior {
                    lowest_prior = a.bayesian_prior;
                    lowest_id = id.clone();
                }
            }
            map.remove(&lowest_id);
        }
        
        map.insert(adapter.id.clone(), Arc::new(adapter));
        Ok(())
    }

    pub fn get_active_adapters(&self) -> Vec<Arc<LoRAAdapter>> {
        let map = self.adapters.read().unwrap();
        map.values().cloned().collect()
    }
}
