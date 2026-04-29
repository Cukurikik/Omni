// Parallax Pipeline Parallelism Layer Shard Manager
// Memory-safe management of model layer partitions across heterogeneous nodes

pub struct OmniResult<T, E> {
    pub value: Option<T>,
    pub error: Option<E>,
}

#[derive(Clone, Debug)]
pub struct LayerShard {
    pub shard_id: u32,
    pub start_layer: u32,
    pub end_layer: u32,
    pub node_id: String,
    pub vram_bytes: u64,
}

pub struct PipelineShardManager {
    shards: Vec<LayerShard>,
    max_shards: u32,
    max_layers: u32,
}

impl PipelineShardManager {
    pub fn new(total_layers: u32) -> OmniResult<Self, String> {
        if total_layers > 256 {
            return OmniResult { value: None, error: Some("Model exceeds 256 layer hard limit".to_string()) };
        }
        OmniResult {
            value: Some(Self {
                shards: Vec::new(),
                max_shards: 128,
                max_layers: total_layers,
            }),
            error: None,
        }
    }

    pub fn assign_shard(&mut self, node_id: &str, start: u32, end: u32, vram: u64) -> OmniResult<u32, String> {
        if self.shards.len() as u32 >= self.max_shards {
            return OmniResult { value: None, error: Some("Max shard capacity reached".to_string()) };
        }
        if end > self.max_layers || start >= end {
            return OmniResult { value: None, error: Some("Invalid layer range".to_string()) };
        }
        // Overlap check
        for s in &self.shards {
            if s.node_id == node_id && !(end <= s.start_layer || start >= s.end_layer) {
                return OmniResult { value: None, error: Some("Layer range overlaps existing shard on node".to_string()) };
            }
        }
        let shard_id = self.shards.len() as u32;
        self.shards.push(LayerShard {
            shard_id,
            start_layer: start,
            end_layer: end,
            node_id: node_id.to_string(),
            vram_bytes: vram,
        });
        OmniResult { value: Some(shard_id), error: None }
    }

    pub fn get_execution_order(&self) -> OmniResult<Vec<u32>, String> {
        let mut order: Vec<&LayerShard> = self.shards.iter().collect();
        order.sort_by_key(|s| s.start_layer);
        let ids: Vec<u32> = order.iter().map(|s| s.shard_id).collect();
        OmniResult { value: Some(ids), error: None }
    }
}
