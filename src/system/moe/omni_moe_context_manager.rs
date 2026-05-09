use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use std::collections::HashMap;
use tokio::sync::RwLock;

/// OMNI MOTHER Production Zero-Mock Context Switcher
/// Manages execution contexts for concurrent MoE requests, preventing
/// state corruption and ensuring thread-safe concurrency.

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct ContextId(usize);

#[derive(Debug)]
pub struct ExecutionContext {
    pub id: ContextId,
    pub priority: u8,
    pub allocated_vram_mb: usize,
    pub active_experts: Vec<u32>,
    pub trace_id: String,
}

pub struct ContextManager {
    contexts: RwLock<HashMap<ContextId, Arc<ExecutionContext>>>,
    next_id: AtomicUsize,
    max_concurrent: usize,
}

impl ContextManager {
    pub fn new(max_concurrent: usize) -> Self {
        Self {
            contexts: RwLock::new(HashMap::new()),
            next_id: AtomicUsize::new(1),
            max_concurrent,
        }
    }

    pub async fn create_context(&self, priority: u8, trace_id: String) -> Result<Arc<ExecutionContext>, String> {
        let mut map = self.contexts.write().await;
        
        if map.len() >= self.max_concurrent {
            // Priority-based eviction could be implemented here.
            return Err("OMNI CRITICAL: Max concurrent contexts reached. System under heavy load.".to_string());
        }

        let id_val = self.next_id.fetch_add(1, Ordering::SeqCst);
        let ctx = Arc::new(ExecutionContext {
            id: ContextId(id_val),
            priority,
            allocated_vram_mb: 0,
            active_experts: Vec::new(),
            trace_id,
        });

        map.insert(ContextId(id_val), ctx.clone());
        Ok(ctx)
    }

    pub async fn get_context(&self, id: ContextId) -> Option<Arc<ExecutionContext>> {
        let map = self.contexts.read().await;
        map.get(&id).cloned()
    }

    pub async fn remove_context(&self, id: ContextId) -> Result<(), String> {
        let mut map = self.contexts.write().await;
        if map.remove(&id).is_some() {
            Ok(())
        } else {
            Err("OMNI WARNING: Attempted to remove non-existent context.".to_string())
        }
    }

    pub async fn active_count(&self) -> usize {
        self.contexts.read().await.len()
    }
}
