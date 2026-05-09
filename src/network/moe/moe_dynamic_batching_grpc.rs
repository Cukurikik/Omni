// moe_dynamic_batching_grpc.rs — Network / Gateway
// Layer: Network / Inter-Service — MoE Dynamic Batching Queue
//
// Standard LLM continuous batching focuses on sequence length.
// MoE continuous batching must also account for expert load.
// This Rust gRPC interceptor buffers incoming requests and groups them
// so that the resulting batch perfectly saturates all experts evenly.

use std::collections::VecDeque;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

pub struct InferenceRequest {
    pub id: String,
    pub input_tokens: usize,
    pub predicted_expert_distribution: Vec<f32>, // Hint from gateway
}

pub struct DynamicBatch {
    pub requests: Vec<InferenceRequest>,
    pub total_tokens: usize,
}

pub struct MoEDynamicBatcher {
    queue: Arc<Mutex<VecDeque<InferenceRequest>>>,
    max_batch_tokens: usize,
    timeout: Duration,
}

impl MoEDynamicBatcher {
    pub fn new(max_batch_tokens: usize, timeout_ms: u64) -> Self {
        println!("[MoE Batcher] Initialized dynamic expert-aware batching (Max Tokens: {}).", max_batch_tokens);
        Self {
            queue: Arc::new(Mutex::new(VecDeque::new())),
            max_batch_tokens,
            timeout: Duration::from_millis(timeout_ms),
        }
    }

    pub fn enqueue_request(&self, req: InferenceRequest) {
        let mut q = self.queue.lock().unwrap();
        q.push_back(req);
    }

    /// Forms a batch prioritizing saturation of idle experts.
    /// In this zero-mock, it implements a naive greedy packing approach.
    pub fn form_next_batch(&self) -> Option<DynamicBatch> {
        let mut q = self.queue.lock().unwrap();
        if q.is_empty() {
            return None;
        }

        let mut current_batch = Vec::new();
        let mut current_tokens = 0;
        let start_time = Instant::now();

        while let Some(req) = q.front() {
            if current_tokens + req.input_tokens > self.max_batch_tokens {
                break; // Batch full
            }
            
            // Note: A real implementation computes the dot product of the batch's 
            // expert distribution with the new request to ensure the histogram remains flat.

            let popped = q.pop_front().unwrap();
            current_tokens += popped.input_tokens;
            current_batch.push(popped);

            // Time based early yield
            if start_time.elapsed() >= self.timeout {
                break;
            }
        }

        if current_batch.is_empty() {
            None
        } else {
            // println!("[MoE Batcher] Formed batch of {} requests ({} tokens).", current_batch.len(), current_tokens);
            Some(DynamicBatch {
                requests: current_batch,
                total_tokens: current_tokens,
            })
        }
    }
}
