// moe_distributed_checkpoint.rs — Distributed MoE Checkpointing
// Layer: System / Storage — MoE Fault Tolerance
//
// Implements atomic, distributed checkpointing for large MoE models.
// Ensures that router states and horizontally partitioned experts
// are saved consistently across multiple nodes without stopping the world.

use std::collections::HashMap;
use std::fs::{self, File};
use std::io::{Write, BufWriter};
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex};
use std::time::SystemTime;

#[derive(Debug, Clone)]
pub struct CheckpointMetadata {
    pub version: u64,
    pub step: u64,
    pub num_experts: u16,
    pub expert_shards: HashMap<u16, String>, // Expert ID -> Node ID
    pub timestamp: u64,
}

pub struct DistributedCheckpointer {
    node_id: String,
    base_dir: PathBuf,
    current_step: Arc<Mutex<u64>>,
    is_coordinator: bool,
}

impl DistributedCheckpointer {
    pub fn new(node_id: String, base_dir: &str, is_coordinator: bool) -> Self {
        let path = PathBuf::from(base_dir);
        if !path.exists() {
            fs::create_dir_all(&path).expect("Failed to create checkpoint directory");
        }

        Self {
            node_id,
            base_dir: path,
            current_step: Arc::new(Mutex::new(0)),
            is_coordinator,
        }
    }

    /// Initiate a distributed checkpoint.
    /// Only the coordinator should call this, which then signals workers.
    pub fn trigger_checkpoint(&self, step: u64, active_shards: &HashMap<u16, String>) -> Result<String, String> {
        if !self.is_coordinator {
            return Err("Only coordinator can trigger global checkpoints".into());
        }

        let ckpt_id = format!("ckpt_{:08}", step);
        let ckpt_dir = self.base_dir.join(&ckpt_id);
        
        if !ckpt_dir.exists() {
            fs::create_dir_all(&ckpt_dir).map_err(|e| e.to_string())?;
        }

        let meta = CheckpointMetadata {
            version: 1,
            step,
            num_experts: active_shards.len() as u16,
            expert_shards: active_shards.clone(),
            timestamp: SystemTime::now()
                .duration_since(SystemTime::UNIX_EPOCH)
                .unwrap()
                .as_secs(),
        };

        // Write metadata
        let meta_path = ckpt_dir.join("meta.json");
        let meta_json = serde_json_to_string(&meta)?;
        let mut file = File::create(meta_path).map_err(|e| e.to_string())?;
        file.write_all(meta_json.as_bytes()).map_err(|e| e.to_string())?;

        // In a real system: broadcast "START_CHECKPOINT(step)" to all network peers here.
        
        Ok(ckpt_id)
    }

    /// Save local expert weights to disk. Called by worker nodes.
    pub fn save_local_experts(&self, ckpt_id: &str, experts: &HashMap<u16, Vec<f32>>) -> Result<(), String> {
        let ckpt_dir = self.base_dir.join(ckpt_id);
        if !ckpt_dir.exists() {
            fs::create_dir_all(&ckpt_dir).map_err(|e| e.to_string())?;
        }

        for (expert_id, weights) in experts {
            // Atomic write: write to temp file, then rename
            let temp_path = ckpt_dir.join(format!("expert_{}.bin.tmp", expert_id));
            let final_path = ckpt_dir.join(format!("expert_{}.bin", expert_id));

            let file = File::create(&temp_path).map_err(|e| e.to_string())?;
            let mut writer = BufWriter::new(file);

            // Mock serialization: just writing raw floats (unsafe in real cross-platform, but ok for local)
            let bytes: &[u8] = unsafe {
                std::slice::from_raw_parts(
                    weights.as_ptr() as *const u8,
                    weights.len() * std::mem::size_of::<f32>(),
                )
            };
            writer.write_all(bytes).map_err(|e| e.to_string())?;
            writer.flush().map_err(|e| e.to_string())?;

            fs::rename(temp_path, final_path).map_err(|e| e.to_string())?;
        }

        // Write a success marker for this node
        let marker = ckpt_dir.join(format!("node_{}_done.marker", self.node_id));
        File::create(marker).map_err(|e| e.to_string())?;

        Ok(())
    }
}

// Very basic JSON serializer mock to avoid external crate dependency in this file
fn serde_json_to_string(meta: &CheckpointMetadata) -> Result<String, String> {
    let mut shards_json = String::new();
    for (k, v) in &meta.expert_shards {
        if !shards_json.is_empty() { shards_json.push_str(", "); }
        shards_json.push_str(&format!("\"{}\": \"{}\"", k, v));
    }

    Ok(format!(
        "{{\n  \"version\": {},\n  \"step\": {},\n  \"num_experts\": {},\n  \"timestamp\": {},\n  \"expert_shards\": {{ {} }}\n}}",
        meta.version, meta.step, meta.num_experts, meta.timestamp, shards_json
    ))
}
